"""
agents/content_agent.py
=======================
Content Researcher & Technical Explanation Agent.
Leverages NVIDIA NIM Nemotron (with offline deterministic fallbacks)
for technical concept extraction, rigorous code examples,
and physical/visual metaphor generation.
"""
from typing import Dict, Any, List, Optional
from ai.nemotron_client import NemotronClient


class ContentAgent:
    def __init__(self, nemotron_client: Optional[NemotronClient] = None):
        self.client = nemotron_client or NemotronClient()

    def generate_explanation(self, topic: str, target_audience: str = "developers") -> Dict[str, Any]:
        """Generates clear, technically precise explanation points."""
        return self.client.explain_technical_concept(topic)

    def generate_code_snippet(self, topic: str, language: str = "python") -> Dict[str, Any]:
        """Generates illustrative minimal code example with highlighting."""
        return self.client.generate_code_snippets(topic, language=language)

    def suggest_visual_metaphor(self, topic: str) -> Dict[str, Any]:
        """Proposes a concrete physical metaphor that maps directly to the technical abstraction."""
        return self.client.generate_visual_metaphor(topic)


    def extract_core_claims(self, topic: str, script_text: str) -> List[str]:
        """Extracts individual testable claims from narration for fact validation."""
        lines = [s.strip() for s in script_text.split(".") if len(s.strip()) > 10]
        return lines[:5]
