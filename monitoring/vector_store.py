from fastembed import TextEmbedding
from qdrant_client import QdrantClient
import uuid


from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from openai import OpenAI

# client = OpenAI()




embedder = TextEmbedding()


qdrant = QdrantClient(
    host="localhost",
    port=6333,
)

COLLECTION_NAME = "document_chunks"


def init_collection(dim: int = 384):
    """
    Create or recreate the vector collection.
    """
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE
            ),
        )
        print("Vector DB collection created.")
    else:
        print("Vector DB collection already exists.")


def embed_text(text: str) -> list[float]:
    
    vector = list(embedder.embed([text]))[0]
    return vector.tolist()


def store_chunk_embedding(document, chunk_index: int, text: str):
    
    
    vector = embed_text(text)
    try:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "document_id": document.id,
                        "chunk_index": chunk_index,
                        "text": text,
                    },
                )
            ],
        )
        print("Vector length:", len(vector))
        print(qdrant.get_collection(COLLECTION_NAME))
    except Exception as e:
        print("QDRANT ERROR:", e)
        raise
    
    return vector
