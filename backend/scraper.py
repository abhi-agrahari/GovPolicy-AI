from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from uuid import uuid4

from chunker import chunk_pages
from vector_store import store_chunks

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: str


@router.post("/scrape")
def scrape_website(request: ScrapeRequest):
    try:
        # make a GET request to the provided URL
        response = requests.get(
            request.url,
            timeout=10,
            headers={
                "User-Agent": "GovPolicy-AI/1.0"
            }
        )

        response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=400,
            detail="Could not access the website."
        )

    soup = BeautifulSoup(response.text, "html.parser")

    # remove elements that usually don't contain useful policy text
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No useful text found on the website."
        )

    pages = [
        {
            "page": 1,
            "text": text
        }
    ]

    chunks = chunk_pages(pages)

    user_id = "demo-user"
    document_id = str(uuid4())

    stored_count = store_chunks(
        chunks,
        request.url,
        user_id,
        document_id
    )

    return {
        "url": request.url,
        "total_chunks": len(chunks),
        "stored_chunks": stored_count,
        "message": "Website scraped and stored successfully"
    }