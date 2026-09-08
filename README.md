# RAG PDF Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that lets you upload a PDF and ask questions about it. Built from scratch over a self-directed 7-day learning plan.

## How it works

1. **Extract** — pulls text out of the uploaded PDF (`pypdf`)
2. **Chunk** — splits the text into overlapping ~500-character pieces
3. **Embed** — converts each chunk into a vector using `BAAI/bge-small-en-v1.5` (`sentence-transformers`)
4. **Store** — saves chunks + vectors in a local vector database (`ChromaDB`)
5. **Retrieve** — finds the most relevant chunks for a given question via semantic search
6. **Generate** — sends the question + retrieved chunks to an LLM (`openai/gpt-oss-20b` via Groq) to produce a grounded answer

## Features

- Upload any PDF and ask questions about it
- Answers are grounded in the document — the model says "I don't know" instead of guessing when the answer isn't present
- **Query decomposition** — compound questions (e.g. "who is X and what are their qualifications") are automatically split into sub-questions, retrieved separately, and combined for a more complete answer
- Custom Streamlit UI with a purple/black glowing theme
- Interactive source-chunk carousel showing exactly which parts of the document an answer was based on
- Chat-style history of the conversation
- "Start over" button to swap in a new PDF without restarting the app

## Tech stack

- Python
- `pypdf` — PDF text extraction
- `sentence-transformers` — embeddings
- `ChromaDB` — vector storage and retrieval
- `Groq` API (`openai/gpt-oss-20b`) — answer generation
- `Streamlit` — web UI

## Running it locally

```bash
pip install -r requirements.txt
```

Set your Groq API key as an environment variable:

```bash
$env:GROQ_API_KEY = "your-key-here"   # PowerShell
```

Then run:

```bash
streamlit run app.py
```

## What I learned

This was a genuinely hands-on introduction to RAG systems, including some real limitations that don't show up in tutorials:

- **Chunking strategy matters** — naive front-matter trimming can accidentally delete the one place a specific fact lives in a document
- **Embedding model choice affects retrieval quality significantly** — switching from `all-MiniLM-L6-v2` to `BAAI/bge-small-en-v1.5` fixed a case where a sparse but important fact wasn't being retrieved at all
- **Compound questions break single-vector retrieval** — one embedding can't represent two distinct information needs well; query decomposition (splitting into sub-questions before retrieving) fixes this
- **Document ambiguity is a real limit** — if a document has two people who could both reasonably be called "the guide," no amount of pipeline tuning fully resolves that; the question itself needs to be more specific
- Always escape any external/document text before injecting it into HTML — unescaped content broke an embedded `<script>` tag and silently killed a UI feature

## Known limitations

- Best suited for questions that map to a specific passage in the document; struggles with purely structural questions (e.g. "what's the first item in this list")
- Answer quality depends on how the question is phrased — semantically similar questions can retrieve different results