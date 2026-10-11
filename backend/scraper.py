from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from dependencies import get_current_user
from urllib.parse import urlsplit, urlunsplit
from vector_store import find_existing_url

from chunker import chunk_pages
from vector_store import store_chunks

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: str


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/") or "/",
        parts.query,
        ""
    ))


@router.post("/scrape")
def scrape_website(request: ScrapeRequest, user_id: str = Depends(get_current_user)):
    # check that the URL is valid
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Please provide a valid URL"
        )
    
    normalized_url = normalize_url(request.url)
    existing = find_existing_url(user_id, normalized_url)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already scraped this website."
        )
    
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

    document_id = str(uuid4())

    stored_count = store_chunks(
        chunks,
        request.url,
        user_id,
        document_id,
        None,
        normalized_url
    )

    return {
        "url": request.url,
        "total_chunks": len(chunks),
        "stored_chunks": stored_count,
        "message": "Website scraped and stored successfully"
    }