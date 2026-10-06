from fastapi import APIRouter

from vector_store import delete_document

router = APIRouter()


@router.delete("/documents/{document_id}")
def delete_document_api(document_id: str):
    user_id = "demo-user"

    delete_document(
        document_id,
        user_id
    )

    return {
        "document_id": document_id,
        "message": "Document deleted successfully"
    }