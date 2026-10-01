from fastapi import FastAPI

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