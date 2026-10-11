from fastapi import Depends
from fastapi import APIRouter
from pydantic import BaseModel
from dependencies import get_current_user

from vector_store import search_chunks
from llm import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    # search Qdrant for relevant policy chunks
    results = search_chunks(
        request.question,
        user_id
    )

    filtered_results = [result for result in results if result['score'] > 0.4]

    if len(filtered_results) == 0:
        return {
            "question": request.question,
            "answer": "No relevant information found in your policies.",
            "sources": []
        }

    # create context from the retrieved chunks
    context = "\n\n".join(
        f"Page {result['page']}:\n{result['text']}"
        for result in filtered_results
    )

    # generate answer using the context and the question
    answer = generate_answer(
        request.question,
        context
    )

    # return answer and sources
    sources = [
        {
            "filename": result["filename"],
            "page": result["page"],
            "score": result["score"]
        }
        for result in filtered_results
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }