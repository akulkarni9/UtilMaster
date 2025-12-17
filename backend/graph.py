import functools
import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from agents.utils import create_agent

from tools.ppt_checker import PPTCheckTool
from tools.ppt_improver import PPTImprovementTool
from tools.word_to_pdf import WordToPDFTool
from tools.pdf_compress import PDFCompressTool
from search_module import HybridSearchTool, CypherSearchTool
import os

# Define the state with full conversation history
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str
    uploaded_files: list[str]  # Track files uploaded in this session

# Initialize LLM
llm = ChatOllama(
    model="llama3.1:8b",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# 1. Worker Agents
ppt_agent = create_agent(
    llm,
    [PPTCheckTool(), PPTImprovementTool()],
    system_prompt=(
        "PowerPoint specialist.\n"
        "- For analyze/check -> use ppt_check_tool\n"
        "- For improve/fix -> use ppt_improvement_tool\n"
        "Both tools accept file_path. Report results briefly."
    )
)

word_agent = create_agent(
    llm,
    [WordToPDFTool()],
    system_prompt=(
        "Convert Word (.docx) to PDF using word_to_pdf_tool.\n"
        "Rules:\n"
        "- Tool accepts: file_path (string)\n"
        "- Tool returns: Markdown link [Download PDF](url)\n"
        "- Your response: Include the EXACT markdown link\n"
        "- Be brief, focus on the download link"
    )
)

pdf_agent = create_agent(
    llm,
    [PDFCompressTool()],
    system_prompt=(
        "Compress PDF files using pdf_compress_tool.\n"
        "Rules:\n"
        "- Tool accepts: file_path (string) for .pdf files ONLY\n"
        "- Tool returns: Markdown link with compression stats\n"
        "- Your response: Include the EXACT markdown link\n"
        "- NO other tools exist, report errors briefly"
    )
)

search_agent = create_agent(
    llm,
    [HybridSearchTool(), CypherSearchTool()],
    system_prompt=(
        "You are a specialist in searching the project database (Neo4j) for information.\n"
        "Tools:\n"
        "- HybridSearchTool: Use this for semantic search about TOPICS (e.g. 'what is X?').\n"
        "- CypherSearchTool: Use this for METADATA or COUNTS (e.g. 'how many files?').\n"
        "Schema Info:\n"
        "- Files are ingested as nodes with label 'Chunk'.\n"
        "- Each Chunk has a property 'source' which is the file path.\n"
        "- To count files, Count DISTINCT 'source' properties on 'Chunk' nodes.\n"
        "Example Cypher: MATCH (n:Chunk) RETURN count(DISTINCT n.source) as file_count"
    )
)

# ChatAgent with GraphRAG capabilities
chat_agent = create_agent(
    llm,
    [HybridSearchTool(), CypherSearchTool()],
    system_prompt=(
        "You are UtilMaster Assistant with access to uploaded files via GraphRAG.\n\n"
        "AVAILABLE CAPABILITIES:\n"
        "1. **PowerPoint**: Analyze PPT files, Improve PPT files (add titles, formatting)\n"
        "2. **PDF**: Compress PDF files\n"
        "3. **Word**: Convert .docx to PDF\n"
        "4. **File Search**: Search uploaded file content and metadata\n\n"
        "TOOL USAGE RULES:\n"
        "- When user asks 'what can you do' or 'help' => List capabilities above WITHOUT using tools\n"
        "- When user asks about file CONTENT ('what's in the file', 'summarize') => Use HybridSearchTool\n"
        "- When user asks for file metadata ('how many files', 'file names') => Use CypherSearchTool\n"
        "- For general chat => Respond directly\n\n"
        "Be friendly and concise."
    )
)

# 2. Supervisor / Orchestrator
members = ["PPTAgent", "WordAgent", "PDFAgent", "SearchAgent", "ChatAgent"]

from langchain_core.messages import ToolMessage

# Helper to run a worker node with tool execution
def run_worker_node(state, agent, tools, name):
    messages = state["messages"]
    # 1. Generate initial response (might contain tool calls)
    response = agent.invoke(messages)
    
    if not response.tool_calls:
        # No tools needed, just return the response
        return {"messages": [response], "next": "Supervisor"}
    
    # 2. Execute tools
    tool_outputs = []
    for tool_call in response.tool_calls:
        selected_tool = next((t for t in tools if t.name == tool_call["name"]), None)
        if selected_tool:
            try:
                print(f"Executing {selected_tool.name} with args: {tool_call['args']}")
                output = selected_tool.invoke(tool_call["args"])
            except Exception as e:
                output = f"Error: {str(e)}"
            
            tool_outputs.append(ToolMessage(
                content=str(output), 
                tool_call_id=tool_call["id"],
                name=selected_tool.name
            ))
    
    # 3. Generate final answer based on tool outputs
    # We append the tool call message + tool results to the history temporarily for generation
    # note: 'agent' is a Runnable (prompt | llm), so we can pass the extended list
    final_response = agent.invoke(messages + [response] + tool_outputs)
    
    # POST-PROCESSING: Ensure markdown links from tool outputs are preserved
    # This compensates for LLM limitations in preserving exact formatting
    import re
    
    # Extract all markdown links from tool outputs
    tool_links = []
    for tool_msg in tool_outputs:
        # Find markdown links: [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', str(tool_msg.content))
        tool_links.extend(links)
    
    # Check if final response is missing these links
    final_content = final_response.content
    missing_links = []
    
    for link_text, link_url in tool_links:
        # If the link isn't in the final response, it was stripped
        if f"[{link_text}]({link_url})" not in final_content:
            missing_links.append(f"[{link_text}]({link_url})")
    
    # Append missing links to the response
    if missing_links:
        final_content = final_content.strip() + "\n\n" + " | ".join(missing_links)
        final_response = AIMessage(content=final_content)
    
    return {"messages": [response] + tool_outputs + [final_response], "next": "Supervisor"}


def supervisor_node(state: AgentState):
    """Context-aware supervisor that routes to appropriate agents"""
    messages = state["messages"]
    
    # Define routing options
    class Router(TypedDict):
        """Choose next agent"""
        next: Literal["PPTAgent", "WordAgent", "PDFAgent", "SearchAgent", "ChatAgent", "FINISH"]
    
    system_prompt = (
        "You are a supervisor orchestrating a multi-agent system for UtilMaster.\n"
        "Your team:\n"
        "- PPTAgent: Analyzes PowerPoint files\n"
        "- WordAgent: Converts Word to PDF\n"
        "- PDFAgent: Compresses PDF files\n"
        "- SearchAgent: Queries the Neo4j database for file metadata and counts\n"
        "- ChatAgent: Handles general conversation AND can retrieve file content using GraphRAG\n\n"
        "Routing rules:\n"
        "1. General questions ('what can you do', 'help', 'hello') -> ChatAgent\n"
        "2. PPT analysis/check -> PPTAgent\n"
        "3. PPT improvement/fix -> PPTAgent\n"
        "4. Word to PDF conversion -> WordAgent\n"
        "5. PDF compression -> PDFAgent\n"
        "6. Database queries about file counts or metadata -> SearchAgent\n"
        "7. Questions about file CONTENT ('what's in the file', 'summarize') -> ChatAgent\n"
        "8. When a worker completes its task -> FINISH\n\n"
        "IMPORTANT: ChatAgent can answer questions without needing file paths."
    )
    
    response = llm.with_structured_output(Router).invoke([
        {"role": "system", "content": system_prompt}
    ] + messages)
    
    return {"next": response["next"]}

# 3. Build Graph
workflow = StateGraph(AgentState)

# Node definitions
workflow.add_node("Supervisor", supervisor_node)

# Use partial to bind specific agent/tools to the generic run_worker_node function
workflow.add_node("PPTAgent", lambda state: run_worker_node(state, ppt_agent, [PPTCheckTool(), PPTImprovementTool()], "PPTAgent"))
workflow.add_node("WordAgent", lambda state: run_worker_node(state, word_agent, [WordToPDFTool()], "WordAgent"))
workflow.add_node("PDFAgent", lambda state: run_worker_node(state, pdf_agent, [PDFCompressTool()], "PDFAgent"))
workflow.add_node("SearchAgent", lambda state: run_worker_node(state, search_agent, [HybridSearchTool(), CypherSearchTool()], "SearchAgent"))
workflow.add_node("ChatAgent", lambda state: run_worker_node(state, chat_agent, [HybridSearchTool(), CypherSearchTool()], "ChatAgent"))

workflow.set_entry_point("Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "PPTAgent": "PPTAgent",
        "WordAgent": "WordAgent",
        "PDFAgent": "PDFAgent",
        "SearchAgent": "SearchAgent",
        "ChatAgent": "ChatAgent",
        "FINISH": END
    }
)

# Connect workers back to supervisor
workflow.add_edge("PPTAgent", "Supervisor")
workflow.add_edge("WordAgent", "Supervisor")
workflow.add_edge("PDFAgent", "Supervisor")
workflow.add_edge("SearchAgent", "Supervisor")
workflow.add_edge("ChatAgent", "Supervisor")

app = workflow.compile()
