import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import re
from collections import Counter




def extract_page_text(page):
    words = page.extract_words(use_text_flow=True)
    words_sorted = sorted(words, key=lambda w: (w['top'], w['x0']))

    lines = []
    current_line = []
    last_top = None

    for w in words_sorted:
        if last_top is None or abs(w['top'] - last_top) < 5:
            current_line.append(w['text'])
        else:
            lines.append(" ".join(current_line))
            current_line = [w['text']]
        last_top = w['top']

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)



def is_low_text(page):
    text = page.extract_text()
    return not text or len(text.strip()) < 50



def clean_text(text):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if len(line) < 3:
            continue
        if re.match(r'^[\W_]+$', line):
            continue
        if re.match(r'^\d+(\s+\d+)*$', line):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)



def remove_repeated_lines(pages):
    all_lines = []
    for p in pages:
        all_lines.extend(p.split("\n"))

    common = {line for line, count in Counter(all_lines).items() if count > 3}

    cleaned_pages = []
    for p in pages:
        lines = [l for l in p.split("\n") if l not in common]
        cleaned_pages.append("\n".join(lines))

    return cleaned_pages



def chunk_text(text, max_len=500):
    sentences = text.split(". ")
    chunks = []
    current = ""

    for s in sentences:
        if len(current) + len(s) < max_len:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "

    if current:
        chunks.append(current.strip())

    return chunks


def process_pdf(file_path):
    pages_text = []
    images = convert_from_path(file_path)

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):

            
            if is_low_text(page):
                text = pytesseract.image_to_string(images[i])
            else:
                text = extract_page_text(page)

            
            text = clean_text(text)
            pages_text.append(text)

    # Remove headers/footers
    pages_text = remove_repeated_lines(pages_text)

   
    output = []
    for i, page_text in enumerate(pages_text):
        chunks = chunk_text(page_text)

        for chunk in chunks:
            output.append({
                "page": i + 1,
                "content": chunk
            })

    return output



def is_crypto_query(query: str) -> bool:
    """Detect if query relates to cryptoassets."""
    crypto_keywords = [
        "crypto", "bitcoin", "ethereum", "token",
        "blockchain", "nft", "defi", "exchange",
        "wallet", "coin", "digital asset"
    ]
    return any(kw in query.lower() for kw in crypto_keywords)
