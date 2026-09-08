from pypdf import PdfReader

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move forward, but re-include the overlap
    return chunks

if __name__ == "__main__":
    text = extract_text("Test.pdf")
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    print("---- Chunk 0 ----")
    print(chunks[5])
    print("---- Chunk 3 ----")
    print(chunks[6])