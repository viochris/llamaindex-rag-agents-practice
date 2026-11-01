import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.node_parser import SentenceSplitter

# ==============================================================================
# 1. ENVIRONMENT CONFIGURATION
# ==============================================================================
# Load environment variables from .env file
load_dotenv()

# Verify if Google API Key is present
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("🚨 [SYSTEM ERROR] GOOGLE_API_KEY is missing. Please check your .env file.")

# Apply Gemini Configuration to LlamaIndex Settings
Settings.llm = Gemini(model="models/gemini-3.6-flash", api_key=GOOGLE_API_KEY)
Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-2", api_key=GOOGLE_API_KEY)
Settings.node_parser = SentenceSplitter(
    chunk_size=512, 
    chunk_overlap=50
)

try: 
    # ==============================================================================
    # 2. DATA INGESTION & CHROMA DB SETUP
    # ==============================================================================
    print("⏳ [SYSTEM] Initializing ChromaDB Persistent Client...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = chroma_client.get_or_create_collection("learning_docs")

    print("🔌 [SYSTEM] Attaching ChromaVectorStore adapter...")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("⏳ [SYSTEM] Loading documents from 'data_dir_example' directory...")
    documents = SimpleDirectoryReader("data_dir_example").load_data()
    print(f"✅ [SYSTEM] Successfully loaded {len(documents)} document(s).")

    print("⚙️ [SYSTEM] Creating Vector Store Index and saving to ChromaDB...")
    index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)
    print("✅ [SYSTEM] Index successfully stored in local ChromaDB.")

    # ==============================================================================
    # 3. QUERY ENGINE & INTERACTIVE PROMPT
    # ==============================================================================
    query_engine = index.as_query_engine()

    print("\n" + "="*70)
    print("💬 [SYSTEM] Interactive session started. Type 'exit' to stop.")
    print("="*70)

    while True:
        # Prompting user for input and removing accidental whitespaces
        user_input = input("\n🗣️ [USER] Enter your question based on the documents: ").strip()
        
        # Termination commands
        if user_input.lower() in ["exit", "close", "out", "break", "keluar"]:
            print("🛑 [SYSTEM] Terminating session. Goodbye!")
            break
            
        # Validating empty user input
        elif not user_input:
            print("⚠️ [SYSTEM] Input cannot be empty. Try again.")
            continue
            
        # Processing valid input
        else:
            print("🧠 [AI] Processing your query...")
            response = query_engine.query(user_input)
            
            # Validating AI response
            if not response:
                print("⚠️ [SYSTEM] AI failed to generate a response or no relevant context found.")
            else:
                # Displaying the final result
                print("-" * 70)
                print("🤖 [AI RESPONSE]:")
                print(response)
                print("-" * 70)

# ==============================================================================
# 4. EXCEPTION HANDLING & ERROR ROUTING
# ==============================================================================
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e).lower()
    error_raw = str(e)

    print("\n" + "="*70)
    print("💥 [CRITICAL FAILURE] LlamaIndex execution aborted!")
    print("-" * 70)

    # 1. Handling API Quota / Rate Limits (Resource Exhausted)
    if error_type == "ResourceExhausted" or "quota" in error_msg or "429" in error_msg:
        print(f"🚨 [API ERROR] {error_type}: Google Gemini API quota exceeded or rate limited. Details: {error_raw}")
        print("="*70 + "\n")

    # 2. Handling Missing Directory / Empty Data
    elif error_type == "ValueError" and "empty" in error_msg:
        print(f"🚨 [DATA ERROR] {error_type}: The data directory is empty or missing valid files. Details: {error_raw}")
        print("="*70 + "\n")

    # 3. Handling API Key / Authentication Issues
    elif error_type == "InvalidArgument" or "api_key" in error_msg:
        print(f"🚨 [AUTH ERROR] {error_type}: Invalid Google API Key configuration. Details: {error_raw}")
        print("="*70 + "\n")
        
    # 4. Handling ChromaDB / SQLite Database Errors
    elif error_type in ["OperationalError", "DatabaseError", "InvalidCollectionException"] or "sqlite" in error_msg or "chroma" in error_msg:
        print(f"🚨 [DATABASE ERROR] {error_type}: ChromaDB failed to initialize or read/write data. (Possible locked file, permission issue, or SQLite version mismatch). Details: {error_raw}")
        print("="*70 + "\n")
        
    # 5. Handling System Permission Errors (Cannot read folder / Cannot write DB)
    elif error_type == "PermissionError":
        print(f"🚨 [ACCESS ERROR] {error_type}: System denied read/write access. Ensure you have permission to read 'data_dir_example' and write to './chroma_db'. Details: {error_raw}")
        print("="*70 + "\n")

    # 6. Fallback for any other unknown errors
    else:
        print(f"🚨 [UNKNOWN ERROR] {error_type}: Unexpected failure during execution. Details: {error_raw}")
        print("="*70 + "\n")