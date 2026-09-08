import os
os.environ["HF_HOME"] = "D:/H/RAG PDF CHATBOT/RAG PDF CHATBOT/hf_cache"

from sentence_transformers import SentenceTransformer
import chromadb
from pdf_utils import extract_text, chunk_text
# Load embedding model (downloads once, then cached locally)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Set up ChromaDB (persistent = saved to disk, not lost when script ends)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="pdf_chunks")

def build_index(pdf_path):
    text = extract_text(pdf_path)
    chunks = chunk_text(text)

    embeddings = model.encode(chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    print(f"Indexed {len(chunks)} chunks.")

def search(query, top_k=5):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results["documents"][0]

from generate import generate_answer

if __name__ == "__main__":
    build_index("Test.pdf")

    query = "what programming language was used for the frontend UI?" or "what is the capital of France?"
    top_chunks = search(query, top_k=5)
    answer = generate_answer(query, top_chunks)

    print(f"\nQuestion: {query}")
    print(f"Answer: {answer}")