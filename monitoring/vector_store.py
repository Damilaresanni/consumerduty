#importing relevant libraries
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
import uuid
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

#initializes the embedding model
embedder = TextEmbedding()

def get_qdrant():
    #creates a Qgrantclient instance by conecting to a Qdrant server on port 6333
    client = QdrantClient(host="localhost", port=6333)
    client.get_collections()  
    return client

#creates a variable COLLECTION_NAME storing the name of the document chunks
COLLECTION_NAME = "document_chunks"

#function for setting up a vector database with d dimension of 384
def init_collection(dim: int = 384):
    #connects to the qdrant client instance
    qdrant = get_qdrant()
    
    #fetches all the collections in the vector databse
    collections = qdrant.get_collections().collections
    
    #checks for all the name in the vector data collection
    existing = [c.name for c in collections]

    #statement to check if the collection already exist
    if COLLECTION_NAME not in existing:
        
        #creates a new collection with set variables and parameters
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE
            ),
        )
        print("Vector DB collection created.")
    else:
       return print("Vector DB collection already exists.")


#This function uses the embedding model to embed the text
def embed_text(text: str) -> list[float]:
    vector = list(embedder.embed([text]))[0]
    return vector.tolist()


def store_chunk_embedding(document, chunk_index: int, text: str):
    #calls and instantiates the get_qdrant client function
    qdrant = get_qdrant()
    #calls the text embedding function for chunking the text
    vector = embed_text(text)
   
   #opens a try/except block
    try:
        #inserts new collection into the database
        qdrant.upsert(
            #defines which data store to save the table into
            collection_name=COLLECTION_NAME,
            points=[
                #defines a vector for each entry into the table
                PointStruct(
                    #sets the id of the each entry using UUID
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
    except Exception as e:
        print("QDRANT ERROR:", e)
        raise
    
    #returns the stored embeddings for logging/debug
    return vector
