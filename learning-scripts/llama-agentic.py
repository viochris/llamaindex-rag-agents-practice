import os
import sys
import asyncio
import chromadb
from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.memory import Memory

# ==============================================================================
# 1. ENVIRONMENT CONFIGURATION
# ==============================================================================
# Load environment variables from the .env file
load_dotenv()

# Verify the presence of the Google API Key before proceeding
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("🚨 [SYSTEM ERROR] GOOGLE_API_KEY is missing. Please check your .env file.")

try: 
    # ==============================================================================
    # 2. SYSTEM SETTINGS & LLM CONFIGURATION
    # ==============================================================================
    print("⚙️ [SYSTEM] Configuring LlamaIndex Settings (LLM & Embeddings)...")
    
    # Configure global LLM and Embedding models using Google Gemini
    Settings.llm = GoogleGenAI(model="models/gemini-3.6-flash", api_key=GOOGLE_API_KEY, temperature=0.3)
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-2", api_key=GOOGLE_API_KEY)
    
    # Configure node parser for chunking documents
    Settings.node_parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )

    # Initialize the Reranker to improve search accuracy by rescoring the top-k retrieved nodes
    print("⚙️ [SYSTEM] Initializing Cross-Encoder Reranker...")
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-2-v2",
        top_n=3
    )

    # ==============================================================================
    # 3. CHROMA DB SETUP (SEPARATED COLLECTIONS)
    # ==============================================================================
    print("⏳ [SYSTEM] Initializing ChromaDB Persistent Client...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    # Create distinct collections to prevent data mixing between different domains
    readme_collection = chroma_client.get_or_create_collection("readme_docs")
    requirements_collection = chroma_client.get_or_create_collection("requirements_docs")

    # Wrap collections into VectorStores and attach them to StorageContexts
    print("🔌 [SYSTEM] Attaching ChromaVectorStore adapters...")
    readme_vector_store = ChromaVectorStore(chroma_collection=readme_collection)
    requirements_vector_store = ChromaVectorStore(chroma_collection=requirements_collection)
    
    readme_storage_context = StorageContext.from_defaults(vector_store=readme_vector_store)
    requirements_storage_context = StorageContext.from_defaults(vector_store=requirements_vector_store)

    # ==============================================================================
    # 4. DATA INGESTION & INDEXING
    # ==============================================================================
    print("⏳ [SYSTEM] Loading documents from local directories...")
    readme_documents = SimpleDirectoryReader("data_dir_example").load_data()
    requirements_documents = SimpleDirectoryReader("data_req_dir_example").load_data()
    print(f"✅ [SYSTEM] Loaded {len(readme_documents)} Readme doc(s) and {len(requirements_documents)} Requirements doc(s).")

    print("⚙️ [SYSTEM] Creating Vector Store Indices and saving to ChromaDB...")
    readme_index = VectorStoreIndex.from_documents(documents=readme_documents, storage_context=readme_storage_context)
    requirements_index = VectorStoreIndex.from_documents(documents=requirements_documents, storage_context=requirements_storage_context)
    print("✅ [SYSTEM] Indices successfully stored in separated ChromaDB collections.")

    # ==============================================================================
    # 5. TOOLS & AGENT INITIALIZATION
    # ==============================================================================
    print("🛠️ [SYSTEM] Initializing Query Engine Tools with Reranker...")
    
    # Define tools equipped with postprocessors (rerankers) for the Agent to use
    tools = [
        QueryEngineTool(
            query_engine=readme_index.as_query_engine(similarity_top_k=5, node_postprocessors=[reranker]),
            metadata=ToolMetadata(
                name="readme_knowledge_tool",
                description="Use this tool to answer general questions about the project's documentation, architecture, and concepts found in the Readme files."
            )
        ),
        QueryEngineTool(
            query_engine=requirements_index.as_query_engine(similarity_top_k=5, node_postprocessors=[reranker]),
            metadata=ToolMetadata(
                name="requirements_tool",
                description="Use this tool to answer questions about the project's dependencies, required packages, and library versions listed in requirements.txt."
            )
        )
    ]

    print("🧠 [SYSTEM] Booting up Function Agent...")
    
    # Define the System Prompt to guide the agent's behavior for technical vs casual queries
    agent_sop = (
        "You are an intelligent technical assistant. "
        "If the user asks a technical question, use the appropriate tools to find the answer. "
        "If the user simply says hello, greets you, or makes casual conversation, "
        "respond directly in a friendly manner WITHOUT trying to use any tools."
    )
    
    # Instantiate the FunctionAgent with the configured tools, LLM, and system prompt
    agent = FunctionAgent(tools=tools, llm=Settings.llm, system_prompt=agent_sop)

    # Initialize conversational memory to maintain context across the session
    memory = Memory.from_defaults(session_id="agentic_session", chat_history=[], token_limit=40000)

    # ==============================================================================
    # 6. ASYNC CHAT LOOP
    # ==============================================================================
    async def main():
        print("\n" + "="*70)
        print("💬 [SYSTEM] Agentic Session Started. Type 'exit' to stop.")
        print("="*70)

        while True:
            # Capture user input from the CLI
            user_input = input("\n🗣️ [USER] You: ").strip()

            # Handle termination commands
            if user_input.lower() in ["exit", "close", "out", "break", "keluar", "x"]:
                print("🛑 [SYSTEM] Terminating session. Goodbye!")
                break
                
            # Guard Clause: Handle empty inputs directly
            if not user_input:
                print("⚠️ [SYSTEM] Input cannot be empty. Please ask a question.")
                continue
                
            # Process valid queries through the Agent, passing the memory state
            print("🧠 [AI] Agent is analyzing the query and routing to the appropriate tool...")
            response = await agent.run(user_msg=user_input, memory=memory)
            
            # Guard Clause: Validate response generation
            if not response:
                print("⚠️ [SYSTEM] Agent failed to generate a response.")
                continue

            # Display the final successful result
            print("-" * 70)
            print("🤖 [AI RESPONSE]:")
            print(response)
            print("-" * 70)
        
    # Execute the async main function
    asyncio.run(main())

# ==============================================================================
# 7. EXCEPTION HANDLING & ERROR ROUTING
# ==============================================================================
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e).lower()
    error_raw = str(e)

    print("\n" + "="*70)
    print("💥 [CRITICAL FAILURE] Agent execution aborted!")
    print("-" * 70)

    # Handle API Rate Limits
    if error_type == "ResourceExhausted" or "quota" in error_msg or "429" in error_msg:
        print(f"🚨 [API ERROR] {error_type}: Google Gemini API quota exceeded or rate limited. Details: {error_raw}")
        
    # Handle missing or empty data directories
    elif error_type == "ValueError" and "empty" in error_msg:
        print(f"🚨 [DATA ERROR] {error_type}: A data directory is empty or missing valid files. Details: {error_raw}")
        
    # Handle Authentication failures
    elif error_type == "InvalidArgument" or "api_key" in error_msg:
        print(f"🚨 [AUTH ERROR] {error_type}: Invalid Google API Key configuration. Details: {error_raw}")
        
    # Handle Local Database/ChromaDB initialization errors
    elif error_type in ["OperationalError", "DatabaseError", "InvalidCollectionException"] or "sqlite" in error_msg or "chroma" in error_msg:
        print(f"🚨 [DATABASE ERROR] {error_type}: ChromaDB initialization failed. Details: {error_raw}")
        
    # Handle File System Permission errors
    elif error_type == "PermissionError":
        print(f"🚨 [ACCESS ERROR] {error_type}: System denied read/write access. Details: {error_raw}")
        
    # Generic fallback for unknown exceptions
    else:
        print(f"🚨 [UNKNOWN ERROR] {error_type}: Unexpected failure. Details: {error_raw}")
        
    print("="*70 + "\n")
    
    # Exit the program gracefully with an error code, hiding the messy traceback
    sys.exit(1)