"""
TextLoom API - Main Application

FastAPI application setup with CORS configuration and router inclusion.
This is the entry point for the TextLoom web API server.

Usage:
    uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import nodes, workspace

# Create FastAPI application
app = FastAPI(
    title="TextLoom API",
    description="REST API for TextLoom node-based text processing system",
    version="1.0.0",
    docs_url="/api/v1/docs",  # Swagger UI
    redoc_url="/api/v1/redoc"  # ReDoc documentation
)

# Configure CORS for local development
# Allow requests from common frontend dev servers
origins = [
    "http://localhost:3000",      # React default
    "http://localhost:5173",      # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8080",      # Alternative port
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(
    nodes.router,
    prefix="/api/v1",
    tags=["nodes"]
)

app.include_router(
    workspace.router,
    prefix="/api/v1",
    tags=["workspace"]
)


# Root endpoint for health check
@app.get("/")
def root():
    """
    API health check endpoint.
    
    Returns basic API information and status.
    """
    return {
        "name": "TextLoom API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/v1/docs"
    }


# API info endpoint
@app.get("/api/v1")
def api_info():
    """
    API version information.
    
    Returns available endpoints and API metadata.
    """
    return {
        "version": "1.0.0",
        "endpoints": {
            "workspace": "/api/v1/workspace",
            "nodes": "/api/v1/nodes",
            "node_detail": "/api/v1/nodes/{session_id}",
            "documentation": "/api/v1/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)