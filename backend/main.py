import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from pdf import router as pdf_router
from search import router as search_router
from scraper import router as scraper_router
from documents import router as documents_router
from auth import router as auth_router

load_dotenv()


app = FastAPI(
    title="GovPolicy AI",
    description="AI-powered government policy assistant"
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to GovPolicy AI!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


app.include_router(
    pdf_router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)


app.include_router(
    search_router,
    prefix="/api/v1",
    tags=["Chat"]
)


app.include_router(
    scraper_router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)


app.include_router(
    documents_router,
    prefix="/api/v1",
    tags=["Documents"]
)