"""
CFA Level 1 Trainer - FastAPI Backend Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .database import init_db
from .routers import users, progress, tests, errors, glossary, calculator, books


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup: Initialize database
    init_db()
    print("Database initialized")
    yield
    # Shutdown: cleanup if needed
    print("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="CFA Level 1 Trainer API",
    description="Backend API for CFA Level 1 exam preparation trainer",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(progress.router)
app.include_router(tests.router)
app.include_router(errors.router)
app.include_router(glossary.router)
app.include_router(calculator.router)
app.include_router(books.router)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "CFA Level 1 Trainer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "exam_date": "2026-05-13"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount static files for frontend (when running together)
# Uncomment when frontend is ready:
# frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
# if os.path.exists(frontend_path):
#     app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
