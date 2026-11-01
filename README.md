# 🦙 LlamaIndex RAG & Agents Practice

Six progressive command-line scripts that walk through LlamaIndex step by step, from a minimal RAG query engine, through chunking, persistence, ChromaDB, and a chat engine with memory, to agents that choose between document collections, plus a clear explanation of why everything here is still local and how to move it to a server.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/Framework-LlamaIndex-6E56CF?style=flat)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-FF6F00?style=flat)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?style=flat&logo=googlegemini&logoColor=white)
![Reranker](https://img.shields.io/badge/Reranker-Cross--Encoder-yellowgreen?style=flat)
![Agents](https://img.shields.io/badge/Agents-FunctionAgent%20%7C%20ReActAgent-black?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## 📌 Overview

This repository collects six standalone Python scripts, kept in the `learning-scripts/` folder, written as hands-on practice with LlamaIndex and as an opening step into the framework. Each script is a complete, runnable command-line app. You point it at a folder of your own documents, it indexes them, and you ask questions in the terminal. Google Gemini generates the answers, using passages retrieved from those documents.

The scripts can be read in order. Script 1 is the simplest possible version. Every later script keeps the same overall shape and adds or swaps a few components: chunking and saved indexes, an external vector database, a chat engine with conversation memory, and finally agents that decide which document collection to search. Because the shape stays the same, you can place two neighbouring scripts side by side and see exactly what changed.

All six scripts follow the same skeleton:

1. Load `.env` and stop with an error if `GOOGLE_API_KEY` is missing.
2. Configure LlamaIndex's global `Settings` (the LLM, the embedding model, and in scripts 2 to 6 the chunking).
3. Read documents from a local folder and build or load an index.
4. Create an engine on top of the index (a query engine, a chat engine, or an agent).
5. Run an interactive loop in the terminal until you type an exit word.
6. If anything fails, print a readable, categorized error message.

This is a learning log, not a finished product. In every script the stored data lives in RAM or on the local disk, never on a server. That is the main limitation of the repository, and it has its own sections below, including the code needed to move to server-based storage.

### 🎓 What You Can Learn From This Repo
* How a minimal RAG application is put together with LlamaIndex (loading, embedding, indexing, querying).
* What chunking is, and how chunk size and overlap are set.
* Three levels of persistence: nothing (RAM), saved index files, and a local vector database.
* The difference between a query engine, a chat engine, and an agent.
* How conversation memory is added, and why RAM-based memory is lost when the script ends.
* How a cross-encoder reranker refines retrieved results.
* How two document collections can be exposed to an agent as separate tools.
* How `FunctionAgent` and `ReActAgent` differ, using the same setup for both.
* Where local storage runs out, and what a server-based setup changes.

### ✨ Key Highlights
* 🪜 **Progressive.** Each script builds on the previous one, so you can see what each new concept adds by comparing two files.
* 🧱 **One shared skeleton.** Environment check, global `Settings`, ingestion, engine, interactive loop, and error handling look the same across all six scripts.
* 🧠 **From query engine to agents.** The scripts move from a stateless query engine, to a context chat engine with memory, to `FunctionAgent` and `ReActAgent` with two query-engine tools.
* 🎯 **Reranking in the agent scripts.** A cross-encoder reranker narrows the top 5 retrieved chunks to the top 3 before they reach the LLM.
* 🛡️ **Categorized error handling.** API quota, data, and authentication errors are routed into readable summary messages in every script, and scripts 3 to 6 add database and permission categories.
* 📋 **Readable console logs.** Every step prints a status line, so you can follow what the script is doing, such as loading documents, indexing, or booting the agent.
* 🔁 **Server-based upgrade path.** A dedicated section shows how to swap local ChromaDB for Chroma Cloud and RAM memory for PostgreSQL-backed memory.

---

## 🎯 Context & Problem Statement

This section explains the problem the repository addresses and how the six scripts map onto it. It is written from what the code shows.

### 🧩 The Problem

A language model on its own knows nothing about your private files. If you ask it about the contents of a README or a requirements file that it has never seen, it can only guess. Retrieval-Augmented Generation (RAG) solves the first part of this: it looks up the relevant pieces of your documents and hands them to the model together with your question. But even after deciding to use RAG with LlamaIndex, a few practical problems appear, and each of them is visible in these scripts.

1. **Too many moving parts at once.** A working LlamaIndex application combines document loading, chunking, embeddings, a vector store, retrieval, generation, memory, and, for agents, tools. Reading all of that in a single large file makes it hard to tell which line is responsible for which behavior.
2. **A first working version forgets everything.** In the simplest setup (script 1) the index lives only in RAM. Every start re-reads and re-embeds all the documents, which costs time and embedding calls, and nothing is kept once the script ends.
3. **A query engine has no conversation.** It treats each question on its own. A follow-up such as "explain that in simpler terms" has nothing to refer to, because the previous answer is not remembered.
4. **One pipeline does not fit every kind of question.** When the documents belong to different categories, such as project documentation and a dependency list, putting everything in one index mixes them. A fixed pipeline also searches the documents even for a plain "hello", when no search is needed.
5. **Everything stays on one machine.** Even with a vector database and memory, local files and RAM cannot be shared with other machines or users, and the conversation disappears when the process ends.

### 💡 The Solution

The repository answers these problems one step at a time, instead of all at once. Each problem above maps to one or two specific scripts. The last column is just as important as the second: it shows what each step still does not solve.

| Problem | Where it is addressed | What the script does | What is still missing |
| :--- | :--- | :--- | :--- |
| 1. Too many parts at once | All six scripts | Each script adds or swaps a few components, so a change can be traced to a single script | The scripts are practice examples, not a complete reference to LlamaIndex |
| 2. A first version forgets everything | Scripts 2 and 3 | Script 2 saves the index to files. Script 3 stores vectors in a local ChromaDB collection | Scripts 3 to 6 do not check for existing data, so documents are embedded again on every start |
| 3. No conversation | Script 4 | A context chat engine with a memory buffer and a strict system prompt | The memory is in RAM and is lost when the script exits |
| 4. One pipeline for every question | Scripts 5 and 6 | Two separate collections become two tools, and an agent decides which one to use, or none for casual messages | The agent's memory is also kept only in the running process |
| 5. Everything on one machine | The server-based sections below | Code to move vectors to Chroma Cloud and memory to PostgreSQL | The snippets have not been run against Chroma Cloud or PostgreSQL from within these six scripts |

Taken together, the scripts do not claim to be a finished application. They are a sequence of small, readable steps, plus an honest list of where each step stops.

---

## 🧠 Core Concepts Explained

If you are new to RAG or LlamaIndex, this table explains the terms used in the rest of the README in plain language.

| Concept | Plain-language explanation | Where you see it |
| :--- | :--- | :--- |
| **RAG** | Retrieval-Augmented Generation. First find the pieces of your documents that are relevant to the question, then give them to the LLM together with the question, so the answer is based on your documents | All six scripts |
| **Document** | A file that has been loaded into memory. `SimpleDirectoryReader` reads the files in a folder and returns documents (usually one per file) | All six scripts |
| **Chunk (node)** | A smaller piece of a document. Long documents are split because searching and prompting work better with short passages | Scripts 2 to 6 set the size explicitly |
| **Chunk size and overlap** | `chunk_size=512` is the target size of each chunk, counted in tokens. `chunk_overlap=50` repeats the last 50 tokens of one chunk at the start of the next, so a sentence cut at the boundary keeps its context | `SentenceSplitter` in scripts 2 to 6 |
| **Embedding** | A list of numbers that represents the meaning of a text. Texts with similar meaning get similar numbers, which is what makes search by meaning possible | `models/gemini-embedding-2` in all scripts |
| **Vector store / index** | The place where chunks and their embeddings are kept so the closest ones can be found quickly | RAM (script 1), files (script 2), ChromaDB (scripts 3 to 6) |
| **Chroma collection** | A named container inside ChromaDB that holds vectors, much like a table in a database. `get_or_create_collection("learning_docs")` opens it, or creates it if it does not exist yet | Scripts 3 to 6 |
| **ChromaVectorStore** | A LlamaIndex adapter around one Chroma collection. It lets LlamaIndex read and write vectors in that collection | Scripts 3 to 6 |
| **StorageContext** | The object that tells an index where its data is kept. `StorageContext.from_defaults(vector_store=...)` builds one that points at a vector store (scripts 3 to 6). `StorageContext.from_defaults(persist_dir=...)` builds one that reads saved files from a folder (script 2) | Scripts 2 to 6 |
| **Retrieval and top-k** | Finding the chunks whose embeddings are closest to the question's embedding. `similarity_top_k=5` means "fetch the 5 closest" | Explicit in scripts 5 and 6, LlamaIndex default elsewhere |
| **Query engine** | Question in, answer out. It retrieves chunks, asks the LLM, and returns the answer. It has no memory of earlier questions | Scripts 1 to 3 |
| **Chat engine (context mode)** | Like a query engine, but it keeps the conversation. For every message it retrieves context, adds it to the prompt, and remembers the exchange | Script 4 |
| **System prompt** | A standing instruction given to the LLM before the conversation, for example "answer only from the provided context" | Scripts 4 to 6 |
| **Memory** | The stored history of the conversation. A token limit (3000 in script 4, 40000 in scripts 5 and 6) caps how much history is kept | Scripts 4 to 6 |
| **Reranker (cross-encoder)** | A second, more careful scoring step. The first search compares embeddings quickly. The cross-encoder then reads the question and each retrieved chunk together and re-scores them, keeping only the best `top_n` | Scripts 5 and 6 (5 fetched, 3 kept) |
| **Tool** | A capability an agent can call. `QueryEngineTool` wraps a query engine with a name and a description, and the agent reads the descriptions to decide which tool fits | Scripts 5 and 6 |
| **Agent** | An LLM that can decide what to do next: call a tool, or answer directly. In these scripts it chooses between two document collections, or none for a greeting | Scripts 5 and 6 |
| **FunctionAgent vs ReActAgent** | Both are agents. A `FunctionAgent` relies on the LLM's built-in tool-calling feature. A `ReActAgent` has the LLM write out its reasoning as text (Thought, Action, Observation) and parses it. A comment in script 6 says the switch was made to prevent JSON parsing errors on casual conversations | Script 5 and script 6 |
| **Settings** | LlamaIndex's global configuration object. Setting `Settings.llm` and `Settings.embed_model` once means every later component uses them | All six scripts |
| **Persistence levels** | **RAM** is lost when the script ends. **Local files** survive but stay on one machine. **A server** survives and can be reached from other machines | See the limitations section |

---

## 🔄 How a Script Works

All six scripts follow the same basic flow. The only parts that change from script to script are where the vectors are stored, which engine answers, and whether there is memory.

```mermaid
flowchart LR
    A["Documents in a local folder"] --> B["SimpleDirectoryReader loads them"]
    B --> C["Chunking, SentenceSplitter in scripts 2 to 6"]
    C --> D["Gemini embedding model turns chunks into vectors"]
    D --> E["Vector store: RAM, saved files, or ChromaDB"]
    Q["Your question in the terminal"] --> R["Question is embedded"]
    R --> S["Retrieve the closest chunks"]
    E --> S
    S --> T["Optional reranker, scripts 5 and 6"]
    T --> U["Gemini LLM reads the chunks and the question"]
    U --> V["Answer printed in the terminal"]
```

In plain words:

1. **Ingest.** Your documents are read, split into chunks, and turned into vectors, then stored. (Script 1 uses default chunking.)
2. **Ask.** Your question is turned into a vector too.
3. **Retrieve.** The store returns the chunks closest in meaning to the question.
4. **Refine (scripts 5 and 6 only).** The reranker re-scores those chunks and keeps the best three.
5. **Generate.** Gemini reads the chunks together with the question and writes the answer.

---

## 🗺️ Learning Path

All six scripts are in the `learning-scripts/` folder. Based on what each script adds on top of the previous one, this is the order in which the concepts build on each other.

```mermaid
flowchart TD
    A["1. llama-basic.py: in-memory index and query engine"] --> B["2. llama-next-storage-chunking.py: chunking and file-based persistence"]
    B --> C["3. llama-advance-chroma-db.py: ChromaDB vector store"]
    C --> D["4. llama-chat-engine.py: context chat engine with memory"]
    D --> E["5. llama-agentic.py: FunctionAgent, two tools, reranker"]
    E --> F["6. llama-react.py: ReActAgent variant"]
    F -.-> G["Next step: server-based storage and memory"]
```

| Step | Script | What gets added | Storage | Memory |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `llama-basic.py` | Gemini LLM and embeddings through `Settings`, `SimpleDirectoryReader`, `VectorStoreIndex`, query engine | RAM | None |
| 2 | `llama-next-storage-chunking.py` | `SentenceSplitter` chunking, persisting and reloading the index | Files in `storage/` | None |
| 3 | `llama-advance-chroma-db.py` | ChromaDB collection through `ChromaVectorStore` and `StorageContext`, broader error handling | Local `./chroma_db` | None |
| 4 | `llama-chat-engine.py` | Context chat engine, system prompt, conversation memory | Local `./chroma_db` | `ChatMemoryBuffer` in RAM |
| 5 | `llama-agentic.py` | Google GenAI integration, reranker, two collections as tools, `FunctionAgent`, async loop | Local `./chroma_db` | `Memory` in the process |
| 6 | `llama-react.py` | `ReActAgent` in place of `FunctionAgent` | Local `./chroma_db` | `Memory` in the process |

### 🔍 What Changes Between Neighbouring Scripts

This is the most direct way to see what each step contributes. It was checked by comparing the files line by line.

| From → To | What changes in the code |
| :--- | :--- |
| 1 → 2 | Adds `SentenceSplitter(chunk_size=512, chunk_overlap=50)`, `PERSIST_DIR = "storage"`, and an `if/else` that either builds and saves the index or loads it with `load_index_from_storage` |
| 2 → 3 | Removes the `storage/` logic. Adds `chromadb.PersistentClient`, a `learning_docs` collection, `ChromaVectorStore`, and passes the `StorageContext` to `from_documents`. Adds database and permission error categories |
| 3 → 4 | Replaces the query engine with `as_chat_engine(chat_mode="context", ...)`. Adds `ChatMemoryBuffer`, a system prompt, and `temperature=0.3`. Uses the `chat_engine_docs` collection. Adds `x` as an exit word and changes the prompt text |
| 4 → 5 | Switches to the `google_genai` integrations. Adds the reranker, two Chroma collections, two `QueryEngineTool`s, a `FunctionAgent`, `Memory`, and an async loop. Removes the chat engine and its memory buffer |
| 5 → 6 | Replaces `FunctionAgent` with `ReActAgent`, calls `agent.run(user_input, memory=memory)` instead of `agent.run(user_msg=user_input, ...)`, and adds `traceback.print_exc()` to the error handler |

You can see any of these differences yourself with a diff tool, for example:
```bash
git diff --no-index learning-scripts/llama-agentic.py learning-scripts/llama-react.py
```

---

## 📚 Script-by-Script Breakdown

### 1️⃣ `llama-basic.py`: the foundation

**Goal.** The simplest of the six scripts: load documents, index them, and answer questions. Everything later builds on this shape.

**What happens when you run it.**
1. Loads `.env` and stops with an error if `GOOGLE_API_KEY` is missing.
2. Sets the LLM and the embedding model in `Settings`.
3. Reads every file in `data_dir_example` with `SimpleDirectoryReader`.
4. Builds a `VectorStoreIndex` from those documents. This is where the embedding calls happen.
5. Creates a query engine and starts the interactive loop.
6. For every question, retrieves relevant chunks and prints Gemini's answer.

**Key code.**
```python
Settings.llm = Gemini(model="models/gemini-3.6-flash", api_key=GOOGLE_API_KEY)
Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-2", api_key=GOOGLE_API_KEY)

documents = SimpleDirectoryReader("data_dir_example").load_data()
index = VectorStoreIndex.from_documents(documents=documents)
query_engine = index.as_query_engine()
```

**Things to try.**
* Ask a question whose answer is in your documents.
* Ask something that is not in your documents, to see how a plain query engine behaves without a strict system prompt (that only appears from script 4).
* Quit and run it again, and notice that the documents are read and embedded all over again.

**Worth knowing.**
* The index only lives in RAM, so it is rebuilt on every run.
* Chunking is left at LlamaIndex's defaults.
* Error handling has four categories: API quota, empty data, authentication, and unknown.
* Exit words: `exit`, `close`, `out`, `break`, `keluar`.

### 2️⃣ `llama-next-storage-chunking.py`: chunking and persistence

**Goal.** Stop rebuilding the index on every run, and set the chunking explicitly.

**What happens when you run it.**
* **First run:** the `storage/` folder does not exist, so the script loads the documents, builds the index, and saves it to `storage/`.
* **Later runs:** the folder exists, so the script skips reading and embedding and loads the saved index.

```text
# first run
⏳ [SYSTEM] Storage 'storage' not found. Loading documents from 'data_dir_example'...
✅ [SYSTEM] Successfully loaded N document(s).
⚙️ [SYSTEM] Creating and persisting Vector Store Index. This may take a moment...
✅ [SYSTEM] Index successfully saved to 'storage' directory.

# later runs
📂 [SYSTEM] Storage 'storage' found. Loading existing index...
✅ [SYSTEM] Index loaded successfully from local storage.
```

**How `StorageContext` is used here.** Every index already has a storage context. On the first run, `index.storage_context.persist(persist_dir=...)` writes it to files in `storage/`. On later runs, `StorageContext.from_defaults(persist_dir=...)` builds a new storage context from those files, and `load_index_from_storage` rebuilds the index from it.

**Key code.**
```python
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

PERSIST_DIR = "storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data_dir_example").load_data()
    index = VectorStoreIndex.from_documents(documents=documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context=storage_context)
```

**Things to try.**
* Run it twice and compare how fast the second start is.
* Add a new file to `data_dir_example` and run it again. The saved index is loaded without the new file. Delete `storage/` to rebuild it.

**Worth knowing.**
* This is file-based storage: a handful of JSON files in `storage/`.
* The only check is whether the `storage/` folder exists. The script cannot tell whether your documents changed.

### 3️⃣ `llama-advance-chroma-db.py`: an external vector database

**Goal.** Keep the vectors in a real vector database (ChromaDB) instead of LlamaIndex's own saved files.

**What happens when you run it.**
1. Opens a local ChromaDB client at `./chroma_db` and gets (or creates) the `learning_docs` collection.
2. Wraps the collection in a `ChromaVectorStore` and a `StorageContext`.
3. Reads the documents, builds the index, and writes the vectors into Chroma.
4. Starts the same query-engine loop as the earlier scripts.

**How the storage pieces connect.** Script 3 is the first script that builds a storage context for a vector store, so it is worth reading step by step.

```mermaid
flowchart LR
    A["PersistentClient: opens the chroma_db folder"] --> B["Collection: learning_docs"]
    B --> C["ChromaVectorStore: LlamaIndex adapter for that collection"]
    C --> D["StorageContext: says where the index keeps its vectors"]
    D --> E["VectorStoreIndex.from_documents(..., storage_context=...)"]
```

1. `chromadb.PersistentClient(path="./chroma_db")` opens the database folder. This is the client.
2. `get_or_create_collection("learning_docs")` opens a collection inside it, the container that holds the vectors.
3. `ChromaVectorStore(chroma_collection=...)` wraps that collection so LlamaIndex can use it as a vector store.
4. `StorageContext.from_defaults(vector_store=vector_store)` creates the storage context, the object that says "this index keeps its vectors in this vector store".
5. `VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)` builds the index and writes the vectors through that storage context. Without the `storage_context` argument, the index would use LlamaIndex's default in-memory store, as in script 1.

**Key code.**
```python
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("learning_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)
```

**Things to try.**
* Add `print(chroma_collection.count())` right after the index is built, run the script twice, and watch the number grow.
* Look inside the `chroma_db/` folder that appears next to the script.

**Worth knowing.**
* Error handling grows to six categories by adding database errors (ChromaDB or SQLite) and permission errors.
* There is no check for existing data. Every run reads, embeds, and writes the documents again, which adds duplicate chunks each time.
* The client is local, so the data stays in one folder on one machine.

### 4️⃣ `llama-chat-engine.py`: conversation with memory

**Goal.** Move from single questions to a conversation, and instruct the model to stay within the documents.

**What happens when you run it.**
1. Sets up the LLM (with `temperature=0.3`), embeddings, and chunking.
2. Opens Chroma and uses the `chat_engine_docs` collection.
3. Creates a `ChatMemoryBuffer` with a 3000-token limit and a strict system prompt.
4. Creates a chat engine in `context` mode and starts the loop, where each message is answered with retrieved context plus the conversation so far.

**Key code.**
```python
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

ai_system_prompt = (
    "You are an intelligent, helpful, and objective AI assistant. "
    "Always base your answers strictly on the provided context documents. "
    "If the answer is not contained within the context, clearly state that you do not know. "
    "Do not hallucinate or invent information."
)

chat_engine = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt=ai_system_prompt
)
```

**Things to try.**
* Ask a question, then a follow-up such as "explain that in simpler terms", and see the answer use the previous turn.
* Ask something that is not in your documents, to see the "say you do not know" instruction at work.
* Quit and start again. The conversation is gone, because the memory buffer lives in RAM.

**Worth knowing.**
* Ingestion runs on every start, as in script 3.
* From this script on, `x` also works as an exit word.

### 5️⃣ `llama-agentic.py`: agents, tools, and reranking

**Goal.** Let an LLM decide which document collection to search, or whether to search at all.

**What happens when you run it.**
1. Switches to the `google_genai` based integrations (`GoogleGenAI`, `GoogleGenAIEmbedding`).
2. Creates the cross-encoder reranker (`top_n=3`).
3. Opens Chroma and creates two collections: `readme_docs` (from `data_dir_example`) and `requirements_docs` (from `data_req_dir_example`). Each collection gets its own `ChromaVectorStore` and its own `StorageContext`, so the two kinds of documents stay separate.
4. Builds an index for each, and wraps each as a `QueryEngineTool` with `similarity_top_k=5` and the reranker attached.
5. Creates a `FunctionAgent` with a system prompt: technical questions go to the tools, greetings are answered directly.
6. Creates a `Memory` object and starts an async loop that calls `agent.run(...)`.

```text
⚙️ [SYSTEM] Configuring LlamaIndex Settings (LLM & Embeddings)...
⚙️ [SYSTEM] Initializing Cross-Encoder Reranker...
⏳ [SYSTEM] Initializing ChromaDB Persistent Client...
🔌 [SYSTEM] Attaching ChromaVectorStore adapters...
⏳ [SYSTEM] Loading documents from local directories...
✅ [SYSTEM] Loaded N Readme doc(s) and M Requirements doc(s).
⚙️ [SYSTEM] Creating Vector Store Indices and saving to ChromaDB...
✅ [SYSTEM] Indices successfully stored in separated ChromaDB collections.
🛠️ [SYSTEM] Initializing Query Engine Tools with Reranker...
🧠 [SYSTEM] Booting up Function Agent...
```

**Key code.**
```python
QueryEngineTool(
    query_engine=readme_index.as_query_engine(similarity_top_k=5, node_postprocessors=[reranker]),
    metadata=ToolMetadata(
        name="readme_knowledge_tool",
        description="Use this tool to answer general questions about the project's documentation, architecture, and concepts found in the Readme files."
    )
)

agent = FunctionAgent(tools=tools, llm=Settings.llm, system_prompt=agent_sop)
memory = Memory.from_defaults(session_id="agentic_session", chat_history=[], token_limit=40000)
response = await agent.run(user_msg=user_input, memory=memory)
```

**Things to try.**
* Say "hello". The system prompt tells the agent to answer greetings directly, without using any tool.
* Ask about the project's architecture, which the `readme_knowledge_tool` description targets.
* Ask which packages the project needs, which the `requirements_tool` description targets.

**Worth knowing.**
* The tool descriptions are what the agent reads to decide, so wording them clearly matters.
* On failure the script prints a categorized message and exits with code 1 without printing the traceback.
* Ingestion again runs on every start, now for both collections.
* On the first run, the reranker model is downloaded.

### 6️⃣ `llama-react.py`: the ReAct variant

**Goal.** Run the same setup as script 5 with a different kind of agent, so the two can be compared.

**What changes from script 5.**
* `ReActAgent` replaces `FunctionAgent`. A comment in the script explains the reason: to prevent JSON parsing errors on casual conversations.
* The agent is called as `agent.run(user_input, memory=memory)`.
* The error handler prints the raw traceback with `traceback.print_exc()` after the categorized message.

**Key code.**
```python
agent = ReActAgent(
    tools=tools,
    llm=Settings.llm,
    system_prompt=agent_sop
)
response = await agent.run(user_input, memory=memory)
```

**Things to try.**
* Ask the same questions you asked in script 5, including a plain greeting, and compare the answers.
* Trigger an error on purpose (for example, a wrong API key) and compare the output of the two error handlers.

**Worth knowing.**
* It reuses the `agentic_session` session id and the same collection names as script 5, so running both from the same folder writes into the same ChromaDB collections.
* Everything stays local, as in the previous scripts.

---

## 🔬 Side-by-Side Comparison

| Script | Gemini integration | Chunking | Storage | Engine | Memory | Reranker |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `Gemini`, `GeminiEmbedding` | LlamaIndex default | In-memory index | Query engine | None | No |
| 2 | `Gemini`, `GeminiEmbedding` | `SentenceSplitter` 512 / 50 | Files in `storage/` | Query engine | None | No |
| 3 | `Gemini`, `GeminiEmbedding` | `SentenceSplitter` 512 / 50 | Local ChromaDB (`learning_docs`) | Query engine | None | No |
| 4 | `Gemini`, `GeminiEmbedding` | `SentenceSplitter` 512 / 50 | Local ChromaDB (`chat_engine_docs`) | Context chat engine | `ChatMemoryBuffer`, 3000 tokens, RAM | No |
| 5 | `GoogleGenAI`, `GoogleGenAIEmbedding` | `SentenceSplitter` 512 / 50 | Local ChromaDB (`readme_docs`, `requirements_docs`) | `FunctionAgent` + 2 tools | `Memory`, 40000 tokens, in the process | Top 5 to top 3 |
| 6 | `GoogleGenAI`, `GoogleGenAIEmbedding` | `SentenceSplitter` 512 / 50 | Local ChromaDB (`readme_docs`, `requirements_docs`) | `ReActAgent` + 2 tools | `Memory`, 40000 tokens, in the process | Top 5 to top 3 |

All six scripts use `models/gemini-3.6-flash` for generation and `models/gemini-embedding-2` for embeddings.

### 🔧 Behavior Details

| Script | Existing data check on start | Error categories | Prints traceback | Exit words | Temperature |
| :---: | :--- | :---: | :---: | :--- | :---: |
| 1 | None, the index is rebuilt in RAM | 4 | No | `exit`, `close`, `out`, `break`, `keluar` | Not set |
| 2 | Checks only whether `storage/` exists | 4 | No | `exit`, `close`, `out`, `break`, `keluar` | Not set |
| 3 | None, documents are embedded again | 6 | No | `exit`, `close`, `out`, `break`, `keluar` | Not set |
| 4 | None, documents are embedded again | 6 | No | Same five, plus `x` | 0.3 |
| 5 | None, both collections are filled again | 6 | No (exits with code 1) | Same five, plus `x` | 0.3 |
| 6 | None, both collections are filled again | 6 | Yes, after the summary | Same five, plus `x` | 0.3 |

---

## 🧩 Tech Stack Highlights

| Layer | Tool | Role |
| :--- | :--- | :--- |
| **Orchestration** | LlamaIndex core (`Settings`, `SimpleDirectoryReader`, `VectorStoreIndex`, `StorageContext`, `SentenceSplitter`) | Global configuration, ingestion, chunking, and indexing |
| **LLM** | `Gemini` (scripts 1 to 4), `GoogleGenAI` (scripts 5 and 6), model `models/gemini-3.6-flash` | Answer generation |
| **Embeddings** | `GeminiEmbedding`, `GoogleGenAIEmbedding`, model `models/gemini-embedding-2` | Embeds document chunks |
| **Vector storage** | LlamaIndex in-memory index, persisted index files, ChromaDB `PersistentClient` | Progresses from RAM, to files, to a local vector database |
| **Reranking** | `SentenceTransformerRerank` (`cross-encoder/ms-marco-MiniLM-L-2-v2`) | Rescores retrieved chunks in the agent scripts |
| **Chat memory** | `ChatMemoryBuffer`, `Memory` | Conversation context in the chat and agent scripts |
| **Agents** | `QueryEngineTool`, `FunctionAgent`, `ReActAgent` | Tool selection over two document collections |
| **Runtime** | `python-dotenv`, `asyncio` | Secrets loading and the async agent loop |

---

## 📁 Repository Structure

```text
llamaindex-rag-agents-practice/
├── learning-scripts/
│   ├── llama-basic.py
│   ├── llama-next-storage-chunking.py
│   ├── llama-advance-chroma-db.py
│   ├── llama-chat-engine.py
│   ├── llama-agentic.py
│   └── llama-react.py
├── LICENSE
├── README.md
└── requirements.txt
```

| Path | Description |
| :--- | :--- |
| `learning-scripts/llama-basic.py` | Step 1. In-memory index and query engine |
| `learning-scripts/llama-next-storage-chunking.py` | Step 2. Chunking and file-based persistence |
| `learning-scripts/llama-advance-chroma-db.py` | Step 3. Local ChromaDB vector store |
| `learning-scripts/llama-chat-engine.py` | Step 4. Context chat engine with a memory buffer |
| `learning-scripts/llama-agentic.py` | Step 5. `FunctionAgent` with two query-engine tools and a reranker |
| `learning-scripts/llama-react.py` | Step 6. `ReActAgent` variant of step 5 |
| `requirements.txt` | All Python dependencies, with notes inside the file |
| `LICENSE` | MIT License |
| `README.md` | You're reading it |

### 📂 Folders You Need to Create

The scripts read their documents from two folders that are **not included in this repository**. Create them yourself inside `learning-scripts/`. The scripts use relative paths, so run them from that folder.

| Folder | Used by | What goes inside |
| :--- | :--- | :--- |
| `data_dir_example/` | All six scripts | Your documents. In scripts 5 and 6 the `readme_knowledge_tool` is described as covering README-style documentation |
| `data_req_dir_example/` | Scripts 5 and 6 | Your documents for the second collection. The `requirements_tool` is described as covering dependencies listed in a `requirements.txt` |

If one of these folders is missing, the script stops with `ValueError: Directory ... does not exist.`

### 🗄️ Folders Created Automatically

You do not create these. The code builds them in the folder where you run the script.

| Folder | Created by | What it holds |
| :--- | :--- | :--- |
| `storage/` | Script 2 | The persisted LlamaIndex index files |
| `chroma_db/` | Scripts 3 to 6 | The local ChromaDB data |

Both are generated data, so they are best kept out of version control.

---

## 💻 Installation & Reproduction Steps

### 📋 Prerequisites
* **Python 3.10 or newer** is required.
* **A Google AI Studio API key** for Gemini.
* **Internet access** on the first run of scripts 5 and 6, to download the cross-encoder reranker weights from Hugging Face.

### 🛠️ CLI Installation & Execution

#### 1. Clone the Repository
```bash
git clone https://github.com/viochris/llamaindex-rag-agents-practice.git
cd llamaindex-rag-agents-practice
```

#### 2. Create and Activate a Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
> The LlamaIndex ecosystem ships as many small, fast-moving sub-packages. If you hit a resolver conflict, try installing into a clean virtual environment and letting `pip` resolve every package from `requirements.txt` in a single command rather than one at a time, since that gives it the full picture needed to pick mutually compatible versions.

#### 4. Configure Environment Variables
Create a `.env` file in the repository root, next to `requirements.txt`. The scripts inside `learning-scripts/` find it automatically.
```env
GOOGLE_API_KEY=your_google_ai_studio_key
```
> Keep `.env` out of version control.

#### 5. Create the Document Folders (required)
Inside `learning-scripts/`, create `data_dir_example/` and put your documents in it. For scripts 5 and 6, also create `data_req_dir_example/` with its own set of documents. See [Folders You Need to Create](#-folders-you-need-to-create).
> Plain text and Markdown files load out of the box. For other formats such as PDF or DOCX, install `llama-index-readers-file` (it is listed as an optional line in `requirements.txt`). Without it, `SimpleDirectoryReader` warns that the package is missing and reads those files as raw text.

#### 6. Run the Scripts in Order
Run them from inside `learning-scripts/`, because the folder paths in the scripts are relative to where you run `python`.
```bash
cd learning-scripts
python llama-basic.py
python llama-next-storage-chunking.py
python llama-advance-chroma-db.py
python llama-chat-engine.py
python llama-agentic.py
python llama-react.py
```
Type your questions at the prompt. Type `exit`, `close`, `out`, `break`, or `keluar` to end a session. Scripts 4, 5, and 6 also accept `x`.

`storage/` and `chroma_db/` are created automatically inside `learning-scripts/` on the first run. To start over, delete `storage/` (script 2) or `chroma_db/` (scripts 3 to 6).

---

## 🛠️ Troubleshooting & Error Messages

### 🚨 Error Categories Printed by the Scripts

When something fails, the scripts print one of these summaries. Which ones exist depends on the script (see Behavior Details above).

| Message prefix | When it is shown | Scripts |
| :--- | :--- | :---: |
| `🚨 [API ERROR]` | The Gemini API reports an exhausted quota, or the error text contains `quota` or `429` | 1 to 6 |
| `🚨 [DATA ERROR]` | A `ValueError` whose message contains the word `empty` | 1 to 6 |
| `🚨 [AUTH ERROR]` | An `InvalidArgument` error, or the error text contains `api_key` | 1 to 6 |
| `🚨 [DATABASE ERROR]` | ChromaDB or SQLite problems, such as a locked file or a version mismatch | 3 to 6 |
| `🚨 [ACCESS ERROR]` | A `PermissionError` when reading a folder or writing the database | 3 to 6 |
| `🚨 [UNKNOWN ERROR]` | Anything that does not match the categories above | 1 to 6 |

### 🧰 Common Problems

| Symptom | Likely cause | What to do |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY is missing` at startup | The `.env` file is missing, or the variable name is wrong | Create `.env` in the repository root with `GOOGLE_API_KEY=...` |
| `ValueError: Directory ... does not exist.` (shown as an unknown error) | `data_dir_example/` or `data_req_dir_example/` was not created, or you ran the script from another folder | Create the folders inside `learning-scripts/` and run the script from there. The `[DATA ERROR]` category only matches messages containing `empty`, so a missing folder is reported as unknown |
| A `FutureWarning` about `google.generativeai` in scripts 1 to 4 | Those scripts use the older Gemini integration | Expected. It is listed under the limitations below |
| `ImportError` asking for `sentence-transformers` or `torch` (scripts 5 and 6) | The dependencies were not installed | Run `pip install -r requirements.txt` in the active virtual environment |
| `ImportError` on `llama_index.core.memory` or `llama_index.core.agent.workflow` | An older `llama-index-core` | `pip install --upgrade llama-index-core` |
| PDF or DOCX files produce strange text | `llama-index-readers-file` is not installed | Install it, as described in step 5 above |
| Script 2 keeps answering from old documents | The saved index in `storage/` is reused | Delete `storage/` and run it again |
| Repeated or near-identical passages in answers (scripts 3 to 6) | A possible cause is duplicate chunks, because every run writes the documents into Chroma again | Delete `chroma_db/` and run the script once |

---

## ⚠️ System Limitations

### 🏗️ The Main Limitation: Storage and Memory Are Not Server-Based
Across the six scripts, everything that gets stored lives either in RAM or in files on the local disk. None of it lives on a server.

| Script | What is stored | Where it lives | What that means |
| :---: | :--- | :--- | :--- |
| 1 | The index | RAM | Lost when the script exits and rebuilt on every run |
| 2 | The index | Files in `storage/` | File-based. Tied to one machine and stale if the documents change |
| 3 | Vectors | Local `./chroma_db` folder | File-based. Tied to one machine and not shared with anyone else |
| 4 | Vectors and conversation | Local `./chroma_db` folder and RAM | Vectors are file-based, and the conversation is lost on exit |
| 5, 6 | Vectors and agent memory | Local `./chroma_db` folder and the running process | Vectors are file-based. No database URI is passed to `Memory`, so the conversation is lost on exit |

In practice this means the data cannot be reached from another machine, cannot be shared between users, and would disappear in any environment where the local disk is temporary. The next section shows how to change that.

### 🔬 Other Limitations Visible in the Code
* **Re-ingestion on every start.** Scripts 3 to 6 have no check for existing data, so documents are re-read, re-embedded, and written into the collection again on each run, which costs embedding calls and adds duplicate chunks. Script 2 only checks whether `storage/` exists.
* **Two generations of Gemini integration.** Scripts 1 to 4 use `llama_index.llms.gemini` and `llama_index.embeddings.gemini`, which are built on the older `google-generativeai` SDK. In a clean environment, importing the Gemini LLM integration prints a `FutureWarning` that support for that SDK has ended. Scripts 5 and 6 use the `google-genai` based integrations.
* **Hardcoded names.** Folder names, collection names, the `storage` path, model names, and the memory session id are fixed values inside each script.
* **No sources shown.** Answers are printed without the chunks or files they were retrieved from.
* **Fixed retrieval settings.** Chunk size, overlap, `similarity_top_k`, and the reranker's `top_n` are fixed values, and the reranker only appears in scripts 5 and 6.
* **Text-based error routing.** Error categories are chosen from exception names and message text, and the handling differs a little between scripts (four categories in scripts 1 and 2, six in scripts 3 to 6, plus a printed traceback only in script 6).
* **No evaluation.** Answer and retrieval quality were not measured against a question set.
* **CLI only.** All interaction happens through a terminal input loop.

---

## 🔁 Moving to Server-Based Storage

### Why Move?

With local storage, the vectors sit in a folder on one computer and the conversation sits in one running process. A server-based setup keeps both on separate services that you reach with credentials. The table shows what changes.

| Aspect | Local (as in this repo) | Server-based (after the upgrade) |
| :--- | :--- | :--- |
| Vectors | `./chroma_db` folder on your machine | Chroma Cloud |
| Conversation memory | RAM or the running process | A PostgreSQL table |
| Vectors after a restart | Kept (scripts 3 to 6) | Kept |
| Conversation after a restart | Lost | Kept |
| Reachable from another machine | No | Yes, with the credentials |
| Credentials needed | `GOOGLE_API_KEY` | Also `CHROMA_API_KEY` and `ASYNCPG_DATABASE_URL` |
| Extra dependency | None | `asyncpg` |

### How to Move

A hosted PostgreSQL database, for example one on Supabase, works as long as you have its connection string. The six scripts in this repository stay local, and the code below shows the changes to make. These snippets have not been run against Chroma Cloud or PostgreSQL from within the six scripts, so test each change after you apply it.

| Script | What to change |
| :---: | :--- |
| 1 | Add a vector store and a storage context. Use the Chroma Cloud setup in step 2 |
| 2 | Replace the persisted `storage/` folder with the Chroma Cloud setup in step 2 and the ingestion guard in step 3 |
| 3 | Swap `PersistentClient` for `CloudClient` and add the ingestion guard |
| 4 | Swap `PersistentClient` for `CloudClient`, add the guard, and replace `ChatMemoryBuffer` with PostgreSQL-backed `Memory` |
| 5, 6 | Swap `PersistentClient` for `CloudClient`, add the guard for both collections, and give `Memory` a database URI |

### 1. Add the credentials
```env
GOOGLE_API_KEY=your_google_ai_studio_key
CHROMA_API_KEY=your_chroma_cloud_key
ASYNCPG_DATABASE_URL=postgresql://user:password@host:port/dbname
```
Install the PostgreSQL driver by uncommenting `asyncpg` in `requirements.txt`, or run `pip install asyncpg`.

### 2. Vector store and storage context: local ChromaDB to Chroma Cloud
Only the first line changes: the client. The collection, the vector store, and the storage context are built in exactly the same way as in the local version.

Scripts 3 and 4. Before:
```python
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("learning_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
```
After:
```python
chroma_client = chromadb.CloudClient(api_key=os.getenv("CHROMA_API_KEY"))
chroma_collection = chroma_client.get_or_create_collection("learning_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
```
Script 4 uses the collection name `chat_engine_docs` instead of `learning_docs`.

What each line does:
1. `CloudClient(api_key=...)` connects to Chroma Cloud with your API key, instead of opening a local folder.
2. `get_or_create_collection(...)` opens the collection on the server, or creates it on the first run.
3. `ChromaVectorStore(...)` wraps that collection so LlamaIndex can use it as a vector store.
4. `StorageContext.from_defaults(vector_store=vector_store)` creates the storage context that tells the index to keep its vectors in that vector store.

Scripts 5 and 6 use two collections, so each one gets its own vector store and storage context:
```python
chroma_client = chromadb.CloudClient(api_key=os.getenv("CHROMA_API_KEY"))

readme_collection = chroma_client.get_or_create_collection("readme_docs")
requirements_collection = chroma_client.get_or_create_collection("requirements_docs")

readme_vector_store = ChromaVectorStore(chroma_collection=readme_collection)
requirements_vector_store = ChromaVectorStore(chroma_collection=requirements_collection)

readme_storage_context = StorageContext.from_defaults(vector_store=readme_vector_store)
requirements_storage_context = StorageContext.from_defaults(vector_store=requirements_vector_store)
```

Scripts 1 and 2 do not build a storage context for a vector store today. To make them server-based, add the lines above (using one collection name of your choice), then create the index with `VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)`. In script 2 you can then drop `PERSIST_DIR`, `persist(...)`, and `load_index_from_storage`, because the vector store itself is now the persistent part.

### 3. Ingestion guard: create the index once, then load it
There are two ways to get an index, and the guard chooses between them:
* **The collection is empty:** read the documents and create the index with `from_documents` and the storage context. This embeds the documents and writes the vectors to the server.
* **The collection already has data:** load the index with `from_vector_store`. This only needs the vector store (not a storage context), and nothing is embedded again.

This also fixes the duplicate-chunk problem described in the limitations. It uses the `vector_store` and `storage_context` variables created in step 2. Scripts 3 and 4:
```python
if chroma_collection.count() == 0:
    print("⏳ [SYSTEM] ChromaDB is empty. Loading documents...")
    documents = SimpleDirectoryReader("data_dir_example").load_data()
    index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)
else:
    print("📂 [SYSTEM] Existing data found in ChromaDB. Bypassing ingestion phase...")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
```
Scripts 5 and 6, once per collection (shown for the README collection, repeat for requirements with `requirements_collection`, `data_req_dir_example`, `requirements_storage_context`, and `requirements_vector_store`):
```python
if readme_collection.count() == 0:
    readme_documents = SimpleDirectoryReader("data_dir_example").load_data()
    readme_index = VectorStoreIndex.from_documents(documents=readme_documents, storage_context=readme_storage_context)
else:
    readme_index = VectorStoreIndex.from_vector_store(vector_store=readme_vector_store)
```
Keep in mind that the guard only checks whether the collection is empty. If your documents change later, the new content is not picked up until the collection is cleared.

### 4. Memory: RAM to PostgreSQL
Script 4, before:
```python
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
```
After (add `from llama_index.core.memory import Memory`):
```python
memory = Memory.from_defaults(
    session_id="chat_engine_session",
    token_limit=3000,
    async_database_uri=os.getenv("ASYNCPG_DATABASE_URL"),
    table_name="llamaindex_chat_memory"
)
```
Scripts 5 and 6, before:
```python
memory = Memory.from_defaults(session_id="agentic_session", chat_history=[], token_limit=40000)
```
After:
```python
memory = Memory.from_defaults(
    session_id="agentic_session",
    token_limit=40000,
    async_database_uri=os.getenv("ASYNCPG_DATABASE_URL"),
    table_name="llamaindex_agent_memory"
)
```
The rest of each script stays as it is. The chat engine still receives `memory=memory`, and the agents still receive it through `agent.run(..., memory=memory)`. The `session_id` and `table_name` values are examples, so choose your own.

After these changes, vectors live in Chroma Cloud and conversations live in PostgreSQL, so neither depends on the local disk or on the running process anymore.

---

## 🚀 Future Work
* **Apply the server-based upgrade.** Move the scripts, or a copy of the last two, to Chroma Cloud and PostgreSQL-backed memory as described above.
* **Add the ingestion guard everywhere.** Stop scripts 3 to 6 from re-embedding the same documents on every run.
* **Unify the Gemini integration.** Move scripts 1 to 4 to the `google-genai` based integrations used in scripts 5 and 6, so the whole repo uses one SDK.
* **Show sources with every answer.** Print the retrieved chunks and their files after each response so answers can be checked.
* **Move configuration out of the code.** Take folder names, collection names, and model names from arguments or environment variables.
* **Evaluate retrieval and answers.** Build a small labeled question set and measure retrieval and answer quality instead of relying on fixed defaults.
* **Add a simple interface.** Replace the terminal loop with a small web interface so the answers and their sources are easier to read.

---

## 📝 Conclusion

The six scripts form a short, readable path through LlamaIndex. Script 1 shows the smallest working RAG loop. Script 2 stops rebuilding the index and sets the chunking. Script 3 moves the vectors into a vector database. Script 4 turns questions into a conversation with memory and a strict system prompt. Scripts 5 and 6 add a reranker and hand two document collections to an agent, first as a `FunctionAgent` and then as a `ReActAgent`. Because every script keeps the same skeleton, each step can be understood by comparing it with the one before it.

The path also reaches a clear limit. Storage and memory in every script are RAM or file based, so nothing survives beyond one machine or, for the conversation, one session, and re-ingestion is not guarded in scripts 3 to 6. The server-based section lists the specific changes that remove those limits, using Chroma Cloud for vectors and PostgreSQL for conversation memory. Until those changes are applied, the repository is best read as a set of practice exercises and a map of where each step stops, not as a finished application.

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
**Author:** [Silvio Christian, Joe](https://github.com/viochris)

*"From a basic query engine to agents, one script at a time."*
