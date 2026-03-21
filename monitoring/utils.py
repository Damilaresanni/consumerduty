from pathlib import Path
from PyPDF2 import PdfReader
import docx


def extract_text(file_path:str) -> str:
    extension = Path(file_path).suffix.lower()
    
    if extension == ".pdf":
        return _extract_text_from_pdf(file_path)
    elif extension in [".docx"]:
        return _extract_text_from_docx(file_path)
    elif extension in [".txt"]:
        return _extract_txt_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")







def _extract_text_from_pdf(file_path):
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

def _extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)

def _extract_txt_text(file_path:str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    # Logic to slide across the text and cut it into pieces
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks