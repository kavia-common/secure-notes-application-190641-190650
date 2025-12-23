from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth_routes import router as auth_router
from src.api.notes_routes import router as notes_router
from src.db import engine
from src.models import Base

openapi_tags = [
    {"name": "health", "description": "Service health checks."},
    {"name": "auth", "description": "Authentication endpoints (signup/login/refresh)."},
    {"name": "notes", "description": "CRUD and search endpoints for user notes."},
]


app = FastAPI(
    title="Secure Notes API",
    description="Backend API for a secure notes application with JWT authentication and user-scoped notes.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS configuration for React dev server on port 3000.
# In production, set CORS_ORIGINS env var accordingly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on startup (simple SQLite setup without migrations)."""
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["health"], summary="Health check")
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


app.include_router(auth_router)
app.include_router(notes_router)
