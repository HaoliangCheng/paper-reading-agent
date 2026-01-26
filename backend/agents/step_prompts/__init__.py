"""Step Prompts Module - Modular prompts for each reading step."""

from .step1_quick_scan import STEP_1_PROMPT
from .step2_context_building import STEP_2_PROMPT
from .step3_methodology import STEP_3_PROMPT
from .step4_critical_analysis import STEP_4_PROMPT
from .step5_math_understanding import STEP_5_PROMPT
from .step6_code_analysis import STEP_6_PROMPT

# All step prompts indexed by step number
STEP_PROMPTS = {
    1: STEP_1_PROMPT,
    2: STEP_2_PROMPT,
    3: STEP_3_PROMPT,
    4: STEP_4_PROMPT,
    5: STEP_5_PROMPT,
    6: STEP_6_PROMPT,
}

__all__ = [
    'STEP_1_PROMPT',
    'STEP_2_PROMPT',
    'STEP_3_PROMPT',
    'STEP_4_PROMPT',
    'STEP_5_PROMPT',
    'STEP_6_PROMPT',
    'STEP_PROMPTS',
]
