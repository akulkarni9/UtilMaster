from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from typing import List

def create_agent(llm: ChatOllama, tools: List, system_prompt: str):
    """Create a function that acts as an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                "\n\n{system_prompt}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    ).partial(system_prompt=system_prompt)
    
    if tools:
        llm = llm.bind_tools(tools)
    
    return prompt | llm
