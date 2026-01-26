"""Conversational Paper Reading Agent Package - Hybrid Design with Modular Steps"""

from .agent import ConversationalPaperAgent
from .prompts import (
    META_SYSTEM_PROMPT,
    STEP_NAMES,
    STEP1_INITIAL_PROMPT,
    get_step_prompt,
    get_step_name,
)
from .tools import create_conversational_tools, create_execute_step_tool
from .image_extractor import OnDemandImageExtractor
from .step_prompts import STEP_PROMPTS

__all__ = [
    'ConversationalPaperAgent',
    'META_SYSTEM_PROMPT',
    'STEP_NAMES',
    'STEP1_INITIAL_PROMPT',
    'STEP_PROMPTS',
    'get_step_prompt',
    'get_step_name',
    'create_conversational_tools',
    'create_execute_step_tool',
    'OnDemandImageExtractor',
]
