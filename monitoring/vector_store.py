# documents/vector_store.py

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from openai import OpenAI

client = OpenAI()

# Connect to local Qdrant (or cloud)
qdrant = QdrantClient(
    host="localhost",
    port=6333,
)

COLLECTION_NAME = "document_chunks"


def init_collection(dim: int = 1536):
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
    """
    Convert text into an embedding vector using OpenAI.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def store_chunk_embedding(document, chunk_index: int, text: str):
    """
    Embed a chunk and store it in Qdrant with metadata.
    """
    vector = embed_text(text)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=f"{document.id}-{chunk_index}",
                vector=vector,
                payload={
                    "document_id": document.id,
                    "product_id": document.product_id,
                    "chunk_index": chunk_index,
                    "text": text,
                },
            )
        ],
    )

    return vector
