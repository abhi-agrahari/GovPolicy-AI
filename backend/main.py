from fastapi import FastAPI
from pdf import router as pdf_router
from search import router as search_router

app = FastAPI(
    title="GovPolicy AI",
    description="AI-powered government policy assistant"
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
    pdf_router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)


app.include_router(
    search_router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)