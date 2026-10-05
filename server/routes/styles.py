"""
server/routes/styles.py
=======================
API endpoints for creative style directives and motion templates.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from server.services.reel_service import ReelService

router = APIRouter(prefix="/api", tags=["styles"])
reel_service = ReelService()


@router.get("/styles")
async def list_styles():
    """Lists all 15 creative directives and design styles."""
    styles = reel_service.get_styles()
    return {
        "status": "success",
        "count": len(styles),
        "styles": styles
    }


@router.get("/styles/{style_id}")
async def get_style(style_id: str):
    """Retrieves the full specification for a specific design style."""
    style = reel_service.get_style(style_id)
    if not style:
        raise HTTPException(status_code=404, detail=f"Style '{style_id}' not found.")
    return {
        "status": "success",
        "style": style
    }
