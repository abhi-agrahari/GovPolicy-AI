from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz
from chunker import chunk_pages

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
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

    try:
        # open the PDF from memory
        document = fitz.open(stream=content, filetype="pdf")

        # extract text from every page
        pages = []
        for page_number, page in enumerate(document, start=1):
            pages.append({
                "page": page_number,
                "text": page.get_text()
            })

        document.close()

        chunks = chunk_pages(pages)

        return {
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF."
        )