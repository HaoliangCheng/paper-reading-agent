"""Conversational Paper Reading Agent - Hybrid Design with Modular Steps"""

import logging
from typing import List, Dict, Any, Callable
from google.genai import types

from .prompts import (
    META_SYSTEM_PROMPT,
    STEP1_INITIAL_PROMPT,
    USER_PROFILE_TEMPLATE,
    STEP_NAMES,
    get_step_prompt,
    get_step_name,
)
from .tools import create_conversational_tools
from .image_extractor import OnDemandImageExtractor

logger = logging.getLogger(__name__)


class ConversationalPaperAgent:
    """
    Conversational paper reading agent with on-demand image extraction.

    Uses generate_content with manual history management for better token control.
    Conversation history is built from database messages.
    """

    def __init__(
        self,
        llm_provider,
        file,
        pdf_path: str,
        paper_folder: str,
        language: str = "English",
        restored_images: List[Dict] = None,
        restored_history: List[Dict[str, str]] = None,
        status_callback = None,
        user_profile: Dict = None,
        add_key_point_callback: Callable[[str], bool] = None
    ):
        """
        Initialize the conversational agent.

        Args:
            llm_provider: LLM provider instance (e.g., GeminiProvider)
            file: Gemini file object (uploaded PDF)
            pdf_path: Path to the PDF file on disk
            paper_folder: Folder to save extracted images
            language: Response language preference
            restored_images: Previously extracted images (for session restore)
            restored_history: Previous conversation history (for session restore)
            status_callback: Optional callback for status updates (e.g., status_callback("Thinking"))
            user_profile: Optional user profile dict with name, background, key_points
            add_key_point_callback: Optional callback to add key points to user profile
        """
        self.llm = llm_provider
        self.client = llm_provider.client
        self.model_id = llm_provider.model_id
        self.file = file
        self.pdf_path = pdf_path
        self.language = language
        self.conversation_history: List[Dict[str, str]] = restored_history or []
        self.system_prompt = None
        self._is_restored = restored_images is not None or restored_history is not None
        self.status_callback = status_callback
        self.user_profile = user_profile or {}
        self.add_key_point_callback = add_key_point_callback

        # Track current reading step (1-6, None means not started)
        self.current_step: int = None

        # Create on-demand image extractor
        self.image_extractor = OnDemandImageExtractor(
            pdf_path=pdf_path,
            paper_folder=paper_folder,
            llm_client=self.client,
            model_id=self.model_id
        )

        # If restoring, load previously extracted images into the extractor
        if restored_images:
            self.image_extractor.extracted_images = restored_images

        # Track extracted images (reference to extractor's list)
        self.extracted_images = self.image_extractor.extracted_images

    def start_session(self) -> str:
        """
        Start the conversational reading session and generate Step 1 automatically.
        If restoring from saved state, just returns the last response.

        Returns:
            Initial Step 1 response from the agent (or last response if restored)
        """
        # If restoring from saved state, just return last assistant response
        if self._is_restored and self.conversation_history:
            logger.info(f"Session restored: {len(self.conversation_history)} messages, {len(self.extracted_images)} images")
            # Try to restore current step from history (default to step 1)
            self.current_step = 1
            for msg in reversed(self.conversation_history):
                if msg["role"] == "assistant":
                    return msg["content"]
            return ""

        # Generate Step 1 automatically with the PDF
        logger.info("Starting new session, generating Step 1...")
        response = self._generate_response(STEP1_INITIAL_PROMPT)

        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def start_session_stream(self):
        """
        Streaming version of start_session.
        """
        if self._is_restored and self.conversation_history:
            self.current_step = 1  # Restore to step 1 by default
            for msg in reversed(self.conversation_history):
                if msg["role"] == "assistant":
                    yield {"response": msg["content"]}
                    return
            yield {"response": ""}
            return

        # Use send_message_stream logic for Step 1
        for update in self.send_message_stream(STEP1_INITIAL_PROMPT):
            if isinstance(update, dict) and 'response' in update:
                # We don't want to duplicate history here because send_message_stream already adds to it
                # and Step 1 is special. But actually send_message_stream adds user prompt too.
                # For Step 1, we might want to keep history clean or handle it specially.
                # Let's just yield it.
                yield update
            else:
                yield update

    def send_message(self, user_message: str) -> str:
        """
        Send a user message and get agent response.

        Args:
            user_message: User's message/question

        Returns:
            Agent's response text
        """
        # Generate response (don't add to history yet - _build_contents handles current message)
        response = self._generate_response(user_message)

        # Now add both user message and response to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def send_message_stream(self, user_message: str):
        """
        Send a user message and yield status updates and final response.
        """
        # We need to capture the status updates. We'll temporarily override status_callback
        original_callback = self.status_callback
        
        def streaming_callback(s):
            self._current_status = s
            if original_callback:
                original_callback(s)

        self.status_callback = streaming_callback
        self._current_status = None

        # Build contents
        contents = self._build_contents(user_message)
        full_system_prompt = self._build_system_prompt()
        tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
        config = types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            tools=tools
        )

        yield "Thinking"
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

        # Handle function calls loop
        max_iterations = 10
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            if not hasattr(response, 'function_calls') or not response.function_calls:
                break

            function_calls = response.function_calls
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            function_response_parts = []
            for fc in function_calls:
                # Yield status for each function
                status_msg = f"Executing: {fc.name}"
                if fc.name == "extract_images":
                    status_msg = "Executing: Extracting figures"
                elif fc.name == "web_search":
                    status_msg = f"Searching web {fc.args.get('query', '')}"
                elif fc.name == "explain_images":
                    status_msg = "Executing: Analyzing figure details"
                elif fc.name == "update_user_profile":
                    status_msg = "Executing: Updating user profile"
                elif fc.name == "execute_step":
                    step_num = fc.args.get('step_number', 1) if fc.args else 1
                    step_name = get_step_name(step_num)
                    status_msg = f"Transitioning to: {step_name}"
                yield status_msg

                result = self._execute_function(fc)
                function_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response=result)
                )

            contents.append(types.Content(role="user", parts=function_response_parts))
            
            # Update tools/config
            tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
            config = types.GenerateContentConfig(system_instruction=self._build_system_prompt(), tools=tools)

            yield "Thinking"
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )

        yield "Generating final response"
        result = self._extract_text_response(response)

        # Update history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        # Reset callback
        self.status_callback = original_callback

        yield {
            "response": result,
            "extracted_images": self.extracted_images
        }

    def _build_system_prompt(self) -> str:
        """Build full system prompt with user profile, current step, and extracted images context."""
        # Build user profile context
        profile_context = self._build_user_profile_context()

        # Build base meta prompt with user profile and language
        base_prompt = META_SYSTEM_PROMPT.format(
            user_profile_context=profile_context,
            language=self.language
        )

        # Add current step's detailed instructions if we're in a step
        if self.current_step:
            step_prompt = get_step_prompt(self.current_step)
            step_name = get_step_name(self.current_step)
            if step_prompt:
                base_prompt += f"\n\n## Current Step: {step_name}\n{step_prompt}"

        # Add extracted images context
        images_context = self._build_extracted_images_context()
        base_prompt += images_context

        return base_prompt

    def _build_user_profile_context(self) -> str:
        """Build context string showing user profile information."""
        if not self.user_profile:
            return ""

        name = self.user_profile.get('name', '')
        key_points = self.user_profile.get('key_points', [])

        if not name and not key_points:
            return ""

        profile_parts = []
        if name:
            profile_parts.append(f"**Name**: {name}")
        if key_points:
            profile_parts.append(f"**Key Insights**: {', '.join(key_points)}")

        profile_content = "\n".join(profile_parts) if profile_parts else "No profile information available."

        return USER_PROFILE_TEMPLATE.format(profile_content=profile_content)

    def _build_extracted_images_context(self) -> str:
        """Build context string showing all extracted images."""
        if not self.extracted_images:
            return "\n\n**Already Extracted Images:** None yet."

        images_list = []
        for i, img in enumerate(self.extracted_images):
            title = img.get('title', 'Untitled')
            page = img.get('page', '?')
            path = img.get('path_relative', '')
            images_list.append(f"  Image {i}: {title} (page {page}) - {path}")

        return "\n\n**Already Extracted Images:**\n" + "\n".join(images_list) + \
               "\n\nUse display_images to show these. Only use extract_images for NEW figures not in this list."

    def _build_contents(self, current_message: str) -> List:
        """
        Build contents array from conversation history and current message.
        Always includes PDF file for context.

        Args:
            current_message: The current user message

        Returns:
            List of Content objects for generate_content
        """
        contents = []

        # Add conversation history (truncate old messages if needed)
        max_history_messages = 20  # Limit history to control tokens
        history_to_use = self.conversation_history[-max_history_messages:] if len(self.conversation_history) > max_history_messages else self.conversation_history

        for msg in history_to_use:
            role = msg["role"]
            content = msg["content"]

            # Truncate very long messages
            if len(content) > 2000:
                content = content[:2000] + "... [truncated]"

            contents.append(types.Content(
                role=role if role == "user" else "model",
                parts=[types.Part.from_text(text=content)]
            ))

        # Add current message with PDF file (always include file for context)
        contents.append(types.Content(
            role="user",
            parts=[
                types.Part.from_uri(file_uri=self.file.uri, mime_type="application/pdf"),
                types.Part.from_text(text=current_message)
            ]
        ))

        return contents

    def _generate_response(self, message: str) -> str:
        """
        Generate response using generate_content with manual history.
        Always includes PDF file for context.

        Args:
            message: User message

        Returns:
            Agent's response text
        """
        # Build contents from history (always includes PDF)
        contents = self._build_contents(message)

        # Build config with system instruction and tools
        full_system_prompt = self._build_system_prompt()
        tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]

        config = types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            tools=tools
        )

        # Generate response
        logger.info(f"→ LLM Request ({len(contents)} content parts)...")
        if self.status_callback:
            self.status_callback("Thinking")

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

        # Handle function calls
        response, contents = self._handle_function_calls(response, contents, config)

        # Extract final text response
        if self.status_callback:
            self.status_callback("Generating final response")
            
        result = self._extract_text_response(response)
        logger.info(f"← LLM Response: {len(result)} chars")
        return result

    def _handle_function_calls(self, response, contents: List, config) -> tuple:
        """
        Handle function calling loop with generate_content.

        Args:
            response: Initial LLM response
            contents: Current contents list
            config: Generate config

        Returns:
            Tuple of (final_response, updated_contents)
        """
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check for function calls
            if not hasattr(response, 'function_calls') or not response.function_calls:
                logger.info(f"✓ Function call loop complete (iteration {iteration})")
                break

            function_calls = response.function_calls
            logger.info(f"⚙ Function Call Round {iteration}: {[fc.name for fc in function_calls]}")

            # Add model's response (with function calls) to contents
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            # Execute all functions and collect responses
            function_response_parts = []
            for idx, fc in enumerate(function_calls):
                logger.info(f"[{idx+1}/{len(function_calls)}] Executing: {fc.name}")
                
                # Update status for each function call
                if self.status_callback:
                    status_msg = f"Executing: {fc.name}"
                    if fc.name == "extract_images":
                        status_msg = "Executing: Extracting figures"
                    elif fc.name == "web_search":
                        status_msg = f"Searching web {fc.args.get('query', '')}"
                    elif fc.name == "explain_images":
                        status_msg = "Executing: Analyzing figure details"
                    elif fc.name == "update_user_profile":
                        status_msg = "Executing: Updating user profile"
                    elif fc.name == "execute_step":
                        step_num = fc.args.get('step_number', 1) if fc.args else 1
                        step_name = get_step_name(step_num)
                        status_msg = f"Transitioning to: {step_name}"
                    self.status_callback(status_msg)

                try:
                    result = self._execute_function(fc)
                    success = result.get('success', 'unknown') if isinstance(result, dict) else 'unknown'
                    logger.info(f"[{idx+1}/{len(function_calls)}] Result: success={success}")

                    function_response_parts.append(
                        types.Part.from_function_response(name=fc.name, response=result)
                    )
                except Exception as e:
                    logger.error(f"[{idx+1}/{len(function_calls)}] ✗ Function failed: {e}", exc_info=True)
                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"success": False, "error": str(e)}
                        )
                    )

            # Add function responses to contents
            contents.append(types.Content(
                role="user",
                parts=function_response_parts
            ))

            # Update config with latest extracted images
            full_system_prompt = self._build_system_prompt()
            tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
            config = types.GenerateContentConfig(
                system_instruction=full_system_prompt,
                tools=tools
            )

            # Generate next response
            logger.info(f"→ Sending function responses to LLM...")
            if self.status_callback:
                self.status_callback("Thinking")
                
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=contents,
                    config=config
                )
                logger.info(f"← LLM response received")
            except Exception as e:
                logger.error(f"✗ Failed to get LLM response: {e}", exc_info=True)
                raise

        if iteration >= max_iterations:
            logger.warning(f"⚠ Function call loop reached max iterations ({max_iterations})")

        return response, contents

    def _execute_function(self, function_call) -> dict:
        """Execute a function call."""
        logger.info(f"🔧 Function: {function_call.name}")
        args = dict(function_call.args) if function_call.args else {}

        # Log arguments (truncate if too long)
        args_str = str(args)
        if len(args_str) > 200:
            logger.debug(f"📋 Args: {args_str[:200]}...")
        else:
            logger.debug(f"📋 Args: {args_str}")

        try:
            if function_call.name == "extract_images":
                images_to_extract = args.get("images", [])
                logger.info(f"📷 Extracting {len(images_to_extract)} new images")

                result = self.image_extractor.extract_images_batch(images_to_extract)

                if result.get("success"):
                    extracted_count = len(result.get('extracted_images', []))
                    logger.info(f"✓ Extracted {extracted_count} images (total: {len(self.extracted_images)})")
                else:
                    logger.warning(f"✗ Extraction failed: {result.get('message', 'Unknown')}")

                return result

            elif function_call.name == "display_images":
                image_indices = args.get("image_indices", [])
                reasoning = args.get("reasoning", "")
                logger.info(f"🖼️ Displaying images: {image_indices}")
                if reasoning:
                    logger.debug(f"💭 Reasoning: {reasoning}")

                markdown_images = []
                for idx in image_indices:
                    if 0 <= idx < len(self.extracted_images):
                        img = self.extracted_images[idx]
                        path = img.get("path_relative", "")
                        title = img.get("title", f"Figure {idx}")
                        markdown_images.append(f"![{title}]({path})")
                    else:
                        logger.warning(f"⚠️ Invalid index {idx}")

                logger.info(f"✓ Prepared {len(markdown_images)} image(s)")

                return {
                    "success": True,
                    "count": len(markdown_images),
                    "markdown_images": markdown_images,
                    "instruction": "Include these images in your response using the markdown above."
                }

            elif function_call.name == "explain_images":
                image_index = args.get("image_index", 0)
                question = args.get("question", "What does this image show?")
                logger.info(f"🔍 Explaining image {image_index}: {question}")

                if image_index < 0 or image_index >= len(self.extracted_images):
                    logger.warning(f"✗ Invalid index {image_index}")
                    return {
                        "success": False,
                        "error": f"Invalid image index {image_index}. Available: 0-{len(self.extracted_images) - 1}"
                    }

                img = self.extracted_images[image_index]
                image_path = img.get("path", "")
                title = img.get("title", f"Figure {image_index}")

                logger.info(f"→ LLM explain: '{title}'")
                try:
                    explanation = self.llm.explain_figure(image_path, question, self.language)
                    logger.info(f"← Explanation: {len(explanation)} chars")

                    return {
                        "success": True,
                        "image_title": title,
                        "question": question,
                        "explanation": explanation,
                        "instruction": "Use this explanation to answer the user's question."
                    }
                except Exception as e:
                    logger.error(f"✗ Explain failed: {e}", exc_info=True)
                    return {"success": False, "error": f"Failed to explain: {str(e)}"}

            elif function_call.name == "web_search":
                query = args.get("query", "")
                context = args.get("context", "")
                logger.info(f"🌐 Web search: {query}")
                if context:
                    logger.debug(f"   Context: {context}")

                if not query:
                    return {"success": False, "error": "No search query provided"}

                try:
                    result = self.llm.web_search(query, self.language)
                    if result.get("success"):
                        sources_count = len(result.get("sources", []))
                        logger.info(f"✓ Search complete: {sources_count} sources")
                    else:
                        logger.warning(f"✗ Search failed: {result.get('error')}")
                    return result
                except Exception as e:
                    logger.error(f"✗ Web search failed: {e}", exc_info=True)
                    return {"success": False, "error": str(e)}

            elif function_call.name == "update_user_profile":
                key_point = args.get("key_point", "")
                logger.info(f"👤 Update user profile: {key_point}")

                if not key_point:
                    return {"success": False, "error": "No key point provided"}

                try:
                    if self.add_key_point_callback:
                        added = self.add_key_point_callback(key_point)
                        if added:
                            # Update local profile as well
                            if 'key_points' not in self.user_profile:
                                self.user_profile['key_points'] = []
                            if key_point not in self.user_profile['key_points']:
                                self.user_profile['key_points'].append(key_point)
                            logger.info(f"✓ Added key point: {key_point}")
                            return {
                                "success": True,
                                "message": f"Added key insight: {key_point}"
                            }
                        else:
                            logger.info(f"⚠ Key point already exists: {key_point}")
                            return {
                                "success": True,
                                "message": "Key insight already recorded"
                            }
                    else:
                        logger.warning("No callback provided for updating user profile")
                        return {
                            "success": False,
                            "error": "Profile update not available"
                        }
                except Exception as e:
                    logger.error(f"✗ Failed to update profile: {e}", exc_info=True)
                    return {"success": False, "error": str(e)}

            elif function_call.name == "execute_step":
                step_number = args.get("step_number", 1)
                reason = args.get("reason", "")
                logger.info(f"📖 Execute step {step_number}: {reason}")

                # Validate step number
                if step_number < 1 or step_number > 6:
                    return {
                        "success": False,
                        "error": f"Invalid step number {step_number}. Must be 1-6."
                    }

                # Get step details
                step_name = get_step_name(step_number)
                step_prompt = get_step_prompt(step_number)

                # Update current step
                previous_step = self.current_step
                self.current_step = step_number

                logger.info(f"✓ Transitioned from step {previous_step} to step {step_number} ({step_name})")

                return {
                    "success": True,
                    "step_number": step_number,
                    "step_name": step_name,
                    "previous_step": previous_step,
                    "reason": reason,
                    "step_instructions": step_prompt,
                    "message": f"Now in Step {step_number}: {step_name}. Follow the step instructions to guide the user."
                }

            else:
                logger.error(f"✗ Unknown function: {function_call.name}")
                return {"success": False, "error": f"Unknown function: {function_call.name}"}

        except Exception as e:
            logger.error(f"✗ Function error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _extract_text_response(self, response) -> str:
        """Extract text from response."""
        if not response.candidates or not response.candidates[0].content.parts:
            return "I apologize, I couldn't generate a response."

        text_parts = []
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                text_parts.append(part.text)

        return ' '.join(text_parts).strip() if text_parts else "I apologize, I couldn't generate a response."

    def get_extracted_images(self) -> List[Dict]:
        """Get list of all extracted images."""
        return self.extracted_images

    def get_current_step(self) -> int:
        """Get the current reading step number (1-6, or None if not started)."""
        return self.current_step

    def get_current_step_name(self) -> str:
        """Get the human-readable name of the current step."""
        if self.current_step:
            return get_step_name(self.current_step)
        return "Not started"

    def set_current_step(self, step_number: int) -> None:
        """
        Manually set the current step (useful for session restoration).

        Args:
            step_number: Step number (1-6)
        """
        if 1 <= step_number <= 6:
            self.current_step = step_number
            logger.info(f"Current step manually set to {step_number} ({get_step_name(step_number)})")
