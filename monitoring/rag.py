from qdrant_client.models import Filter, FieldCondition, MatchValue
from .vector_store import embed_text, get_qdrant, COLLECTION_NAME
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
import os





load_dotenv()
client = OpenAI()
embedder = TextEmbedding()
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "document_chunks"




def search_similar_chunks(query:str,document_id: int ,top_k: int= 10,):
    vector = list(embedder.embed([query]))[0]
                  
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload= True,
        query_filter=Filter(
            must=[FieldCondition(key="document_id", match= MatchValue(value=document_id))]
        )
        
        
    )
    return [
        {
            "score":point.score,
            "text":(point.payload or {}).get("text"),
            "document_id": (point.payload or {}).get("document_id"),
            "chunk_index":(point.payload or {}).get("chunk_index")
        }
        for point in results.points
    ]
    
def rerank_chunks(query, chunks):
    query_words = set(query.lower().split())

    def score(chunk):
        words = set(chunk["text"].lower().split())
        return len(query_words & words)

    return sorted(chunks, key=score, reverse=True)

def filter_findings(query, findings):
    query_words = set(query.lower().split())

    filtered = []
    for f in findings:
        text = (f.snippet or "").lower()
        if any(word in text for word in query_words):
            filtered.append(f)

    return filtered[:5]
  

def build_prompt(query, chunks, findings):
    
    chunks = rerank_chunks(query, chunks)
    
    findings = filter_findings(query, findings)
    
    chunk_text = "\n\n".join(
        f"[Chunk {c['chunk_index']}]\n{c['text']}" for c in chunks
    )

    findings_text = "\n".join(
        f"- {f.rule_name} ({f.fca_rule_ref}): {f.snippet}"
        for f in findings
    )

    return f"""
You are an FCA Consumer Duty compliance assistant.

Instructions:
- Use ONLY the provided context
- If the answer is not clearly supported, say "Not enough information"
- Be precise and reference chunks when relevant

User question:
{query}

Context:
{chunk_text}

Compliance findings:
{findings_text}

Answer:
"""


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an FCA Consumer Duty assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    if not response.choices:
        return ""

    message = response.choices[0].message
    
    return message.content or ""


