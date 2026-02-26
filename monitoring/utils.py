from PyPDF2 import PdfReader

def extract_text(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        # Loop through every page and grab the text
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        
    return text



def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    # Logic to slide across the text and cut it into pieces
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks