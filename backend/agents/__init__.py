"""Conversational Paper Reading Agent Package - Dynamic Stages Architecture"""

from .agent import ConversationalPaperAgent
from .prompts import (
    META_SYSTEM_PROMPT,
    STAGE_NAMES,
    QUICK_SCAN_INITIAL_PROMPT,
    get_stage_prompt,
    get_stage_name,
)
from .tools import create_conversational_tools, create_execute_step_tool
from .image_extractor import OnDemandImageExtractor
from .stage_prompts import STAGE_PROMPTS

__all__ = [
    'ConversationalPaperAgent',
    'META_SYSTEM_PROMPT',
    'STAGE_NAMES',
    'QUICK_SCAN_INITIAL_PROMPT',
    'STAGE_PROMPTS',
    'get_stage_prompt',
    'get_stage_name',
    'create_conversational_tools',
    'create_execute_step_tool',
    'OnDemandImageExtractor',
]
