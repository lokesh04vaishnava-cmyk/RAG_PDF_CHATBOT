import os
os.environ["HF_HOME"] = "D:/H/RAG PDF CHATBOT/RAG PDF CHATBOT/hf_cache"

from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from pdf_utils import extract_text, chunk_text
from generate import generate_answer, decompose_query


class RAGPipeline:
    def __init__(self, db_path="./chroma_db", collection_name="pdf_chunks"):
        self.embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def ingest_pdf(self, pdf_path):
        text = extract_text(pdf_path)
        chunks = chunk_text(text)
        embeddings = self.embedder.encode(chunks).tolist()
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        self.collection.add(documents=chunks, embeddings=embeddings, ids=ids)
        print(f"Ingested '{pdf_path}': {len(chunks)} chunks indexed.")

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=top_k)
        return results["documents"][0]

    def ask(self, question, top_k=8):  # bumped default from 5 to 8
        sub_questions = decompose_query(question, self.groq_client)

        all_chunks = []
        for sq in sub_questions:
            chunks = self.retrieve(sq, top_k=top_k)
            all_chunks.extend(chunks)

        unique_chunks = list(dict.fromkeys(all_chunks))
        return generate_answer(question, unique_chunks, self.groq_client)

    def clear(self):
        self.client.delete_collection(name="pdf_chunks")
        self.collection = self.client.get_or_create_collection(name="pdf_chunks")