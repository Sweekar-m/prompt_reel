"""
server/app.py
=============
FastAPI Application Server for Reel Studio.
Provides REST and SSE endpoints for agents, rendering, styles, and trends,
and serves the React Studio Web Application.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure root workspace is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server.routes import reels, trends, styles

app = FastAPI(
    title="Reel Studio API",
    description="AI-Native Motion Graphics Studio Backend",
    version="2.0.0"
)

# Enable CORS for local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(trends.router)
app.include_router(styles.router)
app.include_router(reels.router)

# Mount Web UI static assets
WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(WEB_DIR, exist_ok=True)

if os.path.exists(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
@app.get("/trends")
@app.get("/templates")
@app.get("/create")
@app.get("/storyboard")
@app.get("/projects")
async def serve_spa():
    """Serves the Single Page Application index for all frontend client routes."""
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "studio": "REEL STUDIO",
        "status": "online",
        "api_docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Reel Studio", "version": "2.0.0"}
