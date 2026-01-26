"""Conversational Agent Tool Definitions - Hybrid Design (Meta Agent + Modular Steps)"""

from typing import List, Dict, Any
from google.genai import types


def create_execute_step_tool() -> types.FunctionDeclaration:
    """Create the execute_step function declaration for step transitions."""
    return types.FunctionDeclaration(
        name="execute_step",
        description="""Transition to a specific reading step. Call this when:
- User is ready to move to the next phase ("let's continue", "next", "move on")
- User explicitly asks for a different step ("show me the math", "find the code")
- User wants to revisit a previous step ("go back to context")
- Starting a new session (call with step 1)

Steps:
1 = Quick Scan (what is this paper?)
2 = Context Building (why does this paper exist?)
3 = Methodology (how do they solve it?)
4 = Critical Analysis (is it still relevant?)
5 = Math Understanding (deep dive into equations)
6 = Code Analysis (implementation details)""",
        parameters={
            "type": "object",
            "properties": {
                "step_number": {
                    "type": "integer",
                    "description": "Step to transition to (1-6)"
                },
                "reason": {
                    "type": "string",
                    "description": "Brief reason for this transition (e.g., 'user asked to continue', 'user wants math details')"
                }
            },
            "required": ["step_number", "reason"]
        }
    )


def create_update_user_profile_tool() -> types.FunctionDeclaration:
    """Create the update_user_profile function declaration."""
    return types.FunctionDeclaration(
        name="update_user_profile",
        description="""Add a key insight about the user based on their questions.

Call this when you learn something significant about the user's:
- Research interests or focus areas
- Technical expertise level
- Background knowledge
- Current projects or goals

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
    Create function declarations for the conversational agent (Hybrid Design).

    Tools:
    1. extract_images - Extract NEW figures from specified pages
    2. display_images - Show already-extracted figures
    3. explain_images - Get detailed explanation of a specific image
    4. web_search - Search web for current information
    5. execute_step - Transition between reading steps
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
        create_execute_step_tool(),  # Add step transition tool
    ]

    if include_profile_tool:
        tools.append(create_update_user_profile_tool())

    return tools
