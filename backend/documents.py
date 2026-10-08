from fastapi import APIRouter, Depends

from vector_store import delete_document, get_user_documents
from dependencies import get_current_user

router = APIRouter()


@router.get("/documents")
def get_documents(user_id: str = Depends(get_current_user)):

    documents = get_user_documents(user_id)

    return {
        "documents": documents
    }



@router.delete("/documents/{document_id}")
def delete_document_api(document_id: str, user_id: str = Depends(get_current_user)):

    delete_document(
        document_id,
        user_id
    )

    return {
        "document_id": document_id,
        "message": "Document deleted successfully"
    }