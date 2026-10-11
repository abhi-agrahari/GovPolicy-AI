from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pymupdf
from chunker import chunk_pages
from vector_store import store_chunks, find_existing_pdf
from uuid import uuid4
from dependencies import get_current_user
import hashlib

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # check file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    # read the uploaded file
    content = await file.read()

    # limit file size to 10 MB
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="PDF must be smaller than 10 MB."
        )

    # check that the file is actually a PDF
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    # check for duplicate uploads by hashing the content
    content_hash = hashlib.sha256(content).hexdigest()

    existing = find_existing_pdf(user_id, content_hash)
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already uploaded this PDF."
        )

    try:
        # open the PDF from memory
        document = pymupdf.open(stream=content, filetype="pdf")

        # extract text from every page
        pages = []
        for page_number, page in enumerate(document, start=1):
            pages.append({
                "page": page_number,
                "text": page.get_text()
            })

        document.close()

        chunks = chunk_pages(pages)

        document_id = str(uuid4())

        stored_count = store_chunks(
            chunks,
            file.filename,
            user_id,
            document_id,
            content_hash,
            None
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "stored_chunks": stored_count,
            "message": "PDF processed and stored successfully"
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF."
        )