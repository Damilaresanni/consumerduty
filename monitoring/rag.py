from qdrant_client.models import Filter, FieldCondition, MatchValue
from .vector_store import embed_text, qdrant, COLLECTION_NAME
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


def search_similar_chunks(query:str,product_id: int ,top_k: int= 5,):
    vector = list(embedder.embed([query]))[0]
                  
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload= True,
        query_filter=Filter(
            must=[FieldCondition(key="product_id", match= MatchValue(value=product_id))]
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
    
    

def build_prompt(query, chunks, findings):
    chunk_text = "\n\n".join(
        f"[Chunk {c['chunk_index']}] {c['text']}" for c in chunks
    )

    findings_text = "\n".join(
        f"- {f.rule_name} ({f.fca_rule_ref}): {f.snippet}"
        for f in findings
    )

    return f"""
You are an FCA Consumer Duty assistant.

User question:
{query}

Relevant document chunks:
{chunk_text}

Relevant FCA findings:
{findings_text}

Answer the question using ONLY the information above.
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


