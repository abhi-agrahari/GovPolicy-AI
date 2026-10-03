from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer


# save Qdrant data in the qdrant_data folder
client = QdrantClient(path="./qdrant_data")

COLLECTION_NAME = "government_policies"

# load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_collection():
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )


def store_chunks(chunks, filename):
    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]

    # convert each text chunk into a vector
    embeddings = model.encode(texts).tolist()

    points = []

    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "filename": filename,
                    "page": chunk["page"],
                    "chunk": chunk["chunk"],
                    "text": chunk["text"]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)


def search_chunks(question, limit=3):
    # convert the user's question into a vector
    question_embedding = model.encode(question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=question_embedding,
        limit=limit,
        with_payload=True
    )

    return [
        {
            "score": result.score,
            "filename": result.payload["filename"],
            "page": result.payload["page"],
            "text": result.payload["text"]
        }
        for result in results.points
    ]


create_collection()