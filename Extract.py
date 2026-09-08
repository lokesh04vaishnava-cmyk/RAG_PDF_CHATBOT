from pypdf import PdfReader

reader = PdfReader("Test.pdf")

full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

print(f"Total pages: {len(reader.pages)}")
print(f"Total characters: {len(full_text)}")
print("---- First 500 chars ----")
print(full_text[:500])