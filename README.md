# GovPolicy AI

An AI-powered government policy assistant that uses Retrieval-Augmented Generation (RAG) to help users understand government policies through document-based and website-based question answering.

## Features

- Upload government policy documents (PDFs) or provide website URLs.
- Ask questions and receive context-aware answers based on uploaded content.
- Generate AI-powered responses grounded in relevant source content, with source references.
- Scrape and ingest government policy websites for information retrieval.
- Implement Google OAuth 2.0 authentication to provide user-specific document access.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API development |
| React | Frontend development |
| Qdrant | Vector database and semantic search |
| Groq API | Large language model inference |
| Sentence Transformers | Text embedding generation |
| Google OAuth 2.0 | User authentication |