from fastapi import APIRouter
from pydantic import BaseModel

from vector_store import search_chunks

router = APIRouter()


class SearchRequest(BaseModel):
    question: str


@router.post("/search")
def search(request: SearchRequest):
    results = search_chunks(request.question)

    return {
        "question": request.question,
        "results": results
    }