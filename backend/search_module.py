import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_ollama import OllamaEmbeddings
from langchain_core.tools import BaseTool
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

class HybridSearchTool(BaseTool):
    name: str = "HybridSearchTool"
    description: str = "Useful for searching the project database for information."

    def _run(self, query: str):
        try:
            embeddings = OllamaEmbeddings(
                model="llama3.1:8b",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            
            neo4j_url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

            # Connect to existing index
            vector_store = Neo4jVector.from_existing_index(
                embedding=embeddings,
                url=neo4j_url,
                username=neo4j_user,
                password=neo4j_password,
                index_name="file_embeddings",
                node_label="Chunk",
                text_node_property="text",
                embedding_node_property="embedding"
            )
            
            results = vector_store.similarity_search(query, k=3)
            return "\n\n".join([doc.page_content for doc in results]) if results else "No relevant information found."
            
        except Exception as e:
            return f"Error searching graph: {str(e)}"

    def _arun(self, query: str):
        raise NotImplementedError("Async not implemented yet")

class CypherSearchTool(BaseTool):
    name: str = "CypherSearchTool"
    description: str = "Useful for running Cypher queries to count items or check metadata in the database. Use this to answer questions like 'how many files'."
    
    def _run(self, query: str):
        try:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            with GraphDatabase.driver(uri, auth=(user, password)) as driver:
                with driver.session() as session:
                    # Safety: Read-only transaction? No, just run it. User is admin locally.
                    result = session.run(query)
                    return str([record.data() for record in result])
        except Exception as e:
            return f"Error running Cypher: {str(e)}"
            
    def _arun(self, query: str):
        raise NotImplementedError("Async not implemented yet")
