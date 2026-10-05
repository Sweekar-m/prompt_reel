"""
server/routes/trends.py
=======================
API endpoints for trend discovery and live research.
"""
from fastapi import APIRouter, Query, Body
from typing import Dict, Any, List, Optional
from agents.research_agent import ResearchAgent

router = APIRouter(prefix="/api", tags=["trends"])
research_agent = ResearchAgent()


@router.get("/trends")
async def get_trends():
    """Returns trending developer topics, AI topics, motion graphics styles, hooks, and formats."""
    topics = research_agent.get_trending_topics()
    styles = research_agent.get_trending_visual_styles()
    hooks = research_agent.get_trending_hooks()
    formats = research_agent.get_trending_creative_formats()

    return {
        "status": "success",
        "tech_topics": [t for t in topics if t.get("category") in ["Developer & Systems", "Languages & Tooling"]],
        "ai_topics": [t for t in topics if t.get("category") == "AI & Modern Architecture"],
        "all_topics": topics,
        "visual_styles": styles,
        "hooks": hooks,
        "formats": formats
    }


@router.post("/research")
async def conduct_research(payload: Dict[str, Any] = Body(...)):
    """Researches a specific user-provided topic with evidence and metrics."""
    topic = payload.get("topic", "How modern caching works")
    result = research_agent.research_topic(topic)
    return {
        "status": "success",
        "research": result
    }
