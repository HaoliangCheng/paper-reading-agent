"""Conversational Agent Tool Definitions - Dynamic Stages Architecture"""

from typing import List, Dict, Any
from google.genai import types


def create_execute_step_tool() -> types.FunctionDeclaration:
    """Create the execute_step function declaration for stage tracking."""
    return types.FunctionDeclaration(
        name="execute_step",
        description="""REQUIRED: Call this tool for EVERY user message to track the current reading stage.

Modes:
1. **Q&A Mode** (mode="qa"): User asks a question, stay in current stage
   - Use when: "What is X?", "Can you explain?", "Tell me more about..."
   - previous_stage and next_stage should be the SAME
   - After this, answer the user's question (don't regenerate stage content)

2. **Transition Mode** (mode="transition"): User wants to move to a different stage
   - Use when: "no questions", "next", "continue", "I understand", "show me the math"
   - previous_stage = current stage, next_stage = new stage to transition to
   - After this, generate the FULL content for the new stage

Available Stages (use the reading_plan in context for this paper's specific stages):
- quick_scan: What is this paper about?
- context_and_contribution: Why does it exist and what did they achieve?
- methodology: How do they solve it? (for single-method papers)
- section_explorer: List sections for user to choose (for multi-section papers)
- section_deep_dive: Explore a specific section (use with section_name)
- math_understanding: Deep dive into equations
- code_analysis: Implementation details""",
        parameters={
            "type": "object",
            "properties": {
                "previous_stage": {
                    "type": "string",
                    "description": "The current stage before this action (e.g., 'quick_scan', 'methodology')"
                },
                "next_stage": {
                    "type": "string",
                    "description": "The stage after this action. Same as previous_stage for Q&A mode, or the new stage for transition mode"
                },
                "mode": {
                    "type": "string",
                    "enum": ["qa", "transition"],
                    "description": "qa = answering question (stay in stage), transition = moving to new stage"
                },
                "reason": {
                    "type": "string",
                    "description": "Brief reason (e.g., 'user asked about attention mechanism', 'user ready to continue')"
                },
                "section_name": {
                    "type": "string",
                    "description": "For section_deep_dive: the name of the section to explore"
                }
            },
            "required": ["previous_stage", "next_stage", "mode", "reason"]
        }
    )


def create_generate_animation_tool() -> types.FunctionDeclaration:
    """Create the generate_animation function declaration for visual explanations."""
    return types.FunctionDeclaration(
        name="generate_animation",
        description="""Generate an interactive HTML/JavaScript animation to explain a complex concept.

Use this tool when:
- The concept involves processes, flows, or sequences that are hard to explain in text
- Mathematical concepts that benefit from visual demonstration (e.g., gradient descent, attention mechanism)
- Architectures or data structures that need interactive visualization
- The user explicitly asks for a visual explanation

The animation should be self-contained HTML with inline CSS and JavaScript.
Create educational animations that help illustrate the concept clearly.""",
        parameters={
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "The concept to explain with animation"
                },
                "animation_html": {
                    "type": "string",
                    "description": "Complete HTML code with inline CSS and JavaScript. Must be a valid self-contained HTML document that can run in an iframe."
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief text explanation to accompany the animation"
                }
            },
            "required": ["concept", "animation_html", "explanation"]
        }
    )


def create_update_user_profile_tool() -> types.FunctionDeclaration:
    """Create the update_user_profile function declaration."""
    return types.FunctionDeclaration(
        name="update_user_profile",
        description="""Add a key insight about the user background and level of expertise.

Call this when you learn something significant about the user's:
- Research interests or focus areas
- Technical expertise level
- Background knowledge

Only add truly relevant insights that would help personalize future explanations.""",
        parameters={
            "type": "object",
            "properties": {
                "key_point": {
                    "type": "string",
                    "description": "A brief insight about the user (keep it concise, 3-10 words)"
                }
            },
            "required": ["key_point"]
        }
    )


def create_conversational_tools(extracted_images: List[Dict] = None, include_profile_tool: bool = True) -> List[types.FunctionDeclaration]:
    """
    Create function declarations for the conversational agent.

    Tools:
    1. extract_images - Extract NEW figures from specified pages
    2. display_images - Show already-extracted figures
    3. explain_images - Get detailed explanation of a specific image
    4. web_search - Search web for current information
    5. execute_step - Transition between reading stages
    6. update_user_profile - Save insights about user (optional)

    Args:
        extracted_images: List of already extracted images with descriptions
        include_profile_tool: Whether to include the user profile tool

    Returns:
        List of FunctionDeclaration objects
    """
    # Build list of already extracted images for display tool
    if extracted_images:
        extracted_list = "\n".join([
            f"Image {i}: {img.get('title', 'Untitled')} (page {img.get('page', '?')})"
            for i, img in enumerate(extracted_images)
        ])
    else:
        extracted_list = "No images extracted yet"

    # Tool 1: Extract NEW images
    extract_images_declaration = types.FunctionDeclaration(
        name="extract_images",
        description="""Extract NEW figures from the PDF that have NOT been extracted yet.

IMPORTANT: Before calling this, check the "Already Extracted Images" list in your context.
If the image you need is already extracted, use display_images instead.

Call this ONLY when you need figures that are NOT in the extracted list.
Provide page numbers and descriptions for the NEW images to extract.""",
        parameters={
            "type": "object",
            "properties": {
                "images": {
                    "type": "array",
                    "description": "List of NEW images to extract",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page_number": {
                                "type": "integer",
                                "description": "The page number (1-indexed) where the figure is located"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the figure to extract"
                            }
                        },
                        "required": ["page_number", "description"]
                    }
                }
            },
            "required": ["images"]
        }
    )

    # Tool 2: Display already-extracted images
    display_images_declaration = types.FunctionDeclaration(
        name="display_images",
        description=f"""Display images that have ALREADY been extracted.

Already Extracted Images:
{extracted_list}

Use this to show images from the list above. Provide the indices of images to display.""",
        parameters={
            "type": "object",
            "properties": {
                "image_indices": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of 0-indexed positions from the extracted images list"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Why showing these images helps explain the concept"
                }
            },
            "required": ["image_indices", "reasoning"]
        }
    )

    # Tool 3: Explain a specific image in detail
    explain_images_declaration = types.FunctionDeclaration(
        name="explain_images",
        description=f"""Get detailed explanation of a specific extracted image.

Use this when the user asks questions about a specific figure/diagram, such as:
- "What does this figure show?"
- "Explain the architecture in Figure 2"
- "What do the arrows mean in this diagram?"

Already Extracted Images:
{extracted_list}

This tool sends the image to a separate LLM call for detailed visual analysis.""",
        parameters={
            "type": "object",
            "properties": {
                "image_index": {
                    "type": "integer",
                    "description": "0-indexed position of the image from the extracted images list"
                },
                "question": {
                    "type": "string",
                    "description": "The specific question to answer about this image"
                }
            },
            "required": ["image_index", "question"]
        }
    )

    # Tool 4: Web search for current information
    web_search_declaration = types.FunctionDeclaration(
        name="web_search",
        description="""Search the web for current information using Google Search.

Use this tool when you need to:
- Verify if a paper's methods are still relevant
- Find more recent related work
- Check current state-of-the-art
- Look up implementation details or code repositories
- Answer questions requiring up-to-date information

This tool uses Google Search grounding to find relevant web sources.""",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                },
                "context": {
                    "type": "string",
                    "description": "Brief context about why this search is needed"
                }
            },
            "required": ["query"]
        }
    )

    tools = [
        extract_images_declaration,
        display_images_declaration,
        explain_images_declaration,
        web_search_declaration,
        create_execute_step_tool(),
        create_generate_animation_tool(),
    ]

    if include_profile_tool:
        tools.append(create_update_user_profile_tool())

    return tools
