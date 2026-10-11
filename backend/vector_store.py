import os

from uuid import uuid4
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue
)
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType

load_dotenv()


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# connect to Qdrant Cloud
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)


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

    indexes = {
        "user_id": PayloadSchemaType.KEYWORD,
        "document_id": PayloadSchemaType.KEYWORD,
        "content_hash": PayloadSchemaType.KEYWORD,
        "source_url": PayloadSchemaType.KEYWORD,
    }

    for field, schema in indexes.items():
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field,
                field_schema=schema,
                wait=True,
            )
        except Exception as e:
            print(f"Error creating index for field '{field}': {e}")



def store_chunks(chunks, filename, user_id, document_id,  content_hash=None, source_url=None):
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
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": filename,
                    "content_hash": content_hash,
                    "source_url": source_url,
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


def search_chunks(question, user_id, limit=3):
    # convert the user's question into a vector
    question_embedding = model.encode(question).tolist()

    # filter to only return results for the current user
    user_filter = Filter(
        must=[
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=question_embedding,
        query_filter=user_filter,
        limit=limit,
        with_payload=True
    )

    return [
        {
            "score": result.score,
            "document_id": result.payload["document_id"],
            "filename": result.payload["filename"],
            "page": result.payload["page"],
            "text": result.payload["text"]
        }
        for result in results.points
    ]


def delete_document(document_id, user_id):
    # delete all points associated with the document_id and user_id
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                ),
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
        )
    )


def get_user_documents(user_id):
    documents = {}

    offset = None

    # traverse through all the points in the collection to get unique document_ids for the user
    while True:
        records, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=100,
            offset=offset,
            with_payload=True
        )

        # process the records to extract unique document_ids and their corresponding filenames
        for record in records:
            payload = record.payload

            document_id = payload["document_id"]

            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "filename": payload["filename"]
                }

        if offset is None:
            break

    return list(documents.values())


create_collection()


def find_existing_pdf(user_id: str, content_hash: str):
    # return an existing PDF document ID if the content hash matches
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                ),
                FieldCondition(
                    key="content_hash",
                    match=MatchValue(value=content_hash)
                )
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=False
    )

    if results:
        return results[0].payload.get("document_id")

    return None


def find_existing_url(user_id: str, normalized_url: str):
    # return an existing website document ID if the URL matches
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                ),
                FieldCondition(
                    key="source_url",
                    match=MatchValue(value=normalized_url)
                )
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=False
    )

    if results:
        return results[0].payload.get("document_id")

    return None
