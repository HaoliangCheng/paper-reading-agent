"""Conversational Paper Reading Agent Package"""

from .agent import ConversationalPaperAgent
from .prompts import CONVERSATIONAL_SYSTEM_PROMPT, STEP_NAMES
from .tools import create_conversational_tools
from .image_extractor import OnDemandImageExtractor

__all__ = [
    'ConversationalPaperAgent',
    'CONVERSATIONAL_SYSTEM_PROMPT',
    'STEP_NAMES',
    'create_conversational_tools',
    'OnDemandImageExtractor'
]
