"""Stage Prompts Module - Modular prompts for each reading stage."""

# Import all stage prompts
from .quick_scan import QUICK_SCAN_SUMMARY_PROMPT, QUICK_SCAN_PLAN_PROMPT, QUICK_SCAN_PROMPT
from .context_building import CONTEXT_BUILDING_PROMPT
from .context_and_contribution import CONTEXT_AND_CONTRIBUTION_PROMPT
from .methodology import METHODOLOGY_PROMPT
from .critical_analysis import CRITICAL_ANALYSIS_PROMPT
from .math_understanding import MATH_UNDERSTANDING_PROMPT
from .code_analysis import CODE_ANALYSIS_PROMPT
from .section_explorer import SECTION_EXPLORER_PROMPT
from .section_deep_dive import SECTION_DEEP_DIVE_PROMPT

# Stage prompts indexed by stage_id
STAGE_PROMPTS = {
    'quick_scan': QUICK_SCAN_PROMPT,
    'context_and_contribution': CONTEXT_AND_CONTRIBUTION_PROMPT,
    'context_building': CONTEXT_BUILDING_PROMPT,  # Alias for backward compatibility
    'methodology': METHODOLOGY_PROMPT,
    'critical_analysis': CRITICAL_ANALYSIS_PROMPT,
    'math_understanding': MATH_UNDERSTANDING_PROMPT,
    'code_analysis': CODE_ANALYSIS_PROMPT,
    'section_explorer': SECTION_EXPLORER_PROMPT,
    'section_deep_dive': SECTION_DEEP_DIVE_PROMPT,
}


def get_stage_prompt(stage_id: str) -> str:
    """Get prompt for a stage by its ID."""
    return STAGE_PROMPTS.get(stage_id, '')


__all__ = [
    # Quick scan prompts (split for parallel execution)
    'QUICK_SCAN_SUMMARY_PROMPT',
    'QUICK_SCAN_PLAN_PROMPT',
    'QUICK_SCAN_PROMPT',
    # Other stage prompts
    'CONTEXT_BUILDING_PROMPT',
    'CONTEXT_AND_CONTRIBUTION_PROMPT',
    'METHODOLOGY_PROMPT',
    'CRITICAL_ANALYSIS_PROMPT',
    'MATH_UNDERSTANDING_PROMPT',
    'CODE_ANALYSIS_PROMPT',
    'SECTION_EXPLORER_PROMPT',
    'SECTION_DEEP_DIVE_PROMPT',
    # Stage prompts dict
    'STAGE_PROMPTS',
    'get_stage_prompt',
]
