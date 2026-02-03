from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .paper import PaperAnalysis


@dataclass
class ReadingSessionState:
    """Tracks the state of a paper reading session"""
    session_id: str
    paper_id: str
    current_step: int = 1
    completed_steps: List[int] = field(default_factory=list)
    paper_analysis: Optional[PaperAnalysis] = None
    comprehension_score: float = 0.0
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
