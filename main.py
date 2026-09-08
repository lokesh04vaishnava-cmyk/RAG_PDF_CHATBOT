from rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

# Only run this once per PDF — comment it out after first run
pipeline.ingest_pdf("Test.pdf")

while True:
    question = input("\nAsk something about the PDF (or 'quit'): ")
    if question.lower() == "quit":
        break
    answer = pipeline.ask(question)
    print(f"Answer: {answer}")
