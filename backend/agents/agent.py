"""Conversational Paper Reading Agent - Dynamic Stages with Parallel Quick Scan"""

import logging
import concurrent.futures
from typing import List, Dict, Any, Callable
from google.genai import types

from .prompts import (
    META_SYSTEM_PROMPT,
    QUICK_SCAN_INITIAL_PROMPT,
    USER_PROFILE_TEMPLATE,
    STAGE_NAMES,
    get_stage_prompt,
    get_stage_name,
    QUICK_SCAN_SUMMARY_PROMPT,
    QUICK_SCAN_PLAN_PROMPT,
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

        # Track current stage ID (string) - dynamic system
        self.current_stage_id: str = None

        # Store the dynamic reading plan from Quick Scan
        self.reading_plan: list = []

        # Track which section is being explored (for section_deep_dive)
        self.current_section: str = None

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
        Start the conversational reading session and generate Quick Scan automatically.
        If restoring from saved state, just returns the last response.

        Returns:
            Initial Quick Scan response from the agent (or last response if restored)
        """
        # If restoring from saved state, just return last assistant response
        if self._is_restored and self.conversation_history:
            logger.info(f"Session restored: {len(self.conversation_history)} messages, {len(self.extracted_images)} images")
            self.current_stage_id = 'quick_scan'
            for msg in reversed(self.conversation_history):
                if msg["role"] == "assistant":
                    return msg["content"]
            return ""

        # Start at Quick Scan stage
        self.current_stage_id = 'quick_scan'
        logger.info("Starting new session at Quick Scan stage...")
        response = self._generate_response(QUICK_SCAN_INITIAL_PROMPT)

        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def start_session_stream(self):
        """
        Streaming version of start_session with parallel Quick Scan.
        Runs summary generation (with tools) and plan generation (JSON only) in parallel.
        """
        if self._is_restored and self.conversation_history:
            self.current_stage_id = 'quick_scan'
            for msg in reversed(self.conversation_history):
                if msg["role"] == "assistant":
                    yield {"response": msg["content"]}
                    return
            yield {"response": ""}
            return

        # Start at Quick Scan stage
        self.current_stage_id = 'quick_scan'
        logger.info("Starting new session at Quick Scan stage [streaming with parallel requests]")

        yield "Analyzing paper"

        # Run summary and plan generation in parallel
        summary_result = None
        plan_result = None

        def generate_summary():
            """Generate summary with tools (text output)."""
            return self._generate_quick_scan_summary()

        def generate_plan():
            """Generate plan without tools (JSON output)."""
            return self._generate_quick_scan_plan()

        yield "Running parallel analysis"

        # Execute both requests in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            summary_future = executor.submit(generate_summary)
            plan_future = executor.submit(generate_plan)

            # Wait for both to complete
            summary_result = summary_future.result()
            plan_result = plan_future.result()

        yield "Combining results"

        # Combine results - summary becomes the response, plan contains the reading plan
        final_response = summary_result.get('summary', '')
        extracted_images = summary_result.get('extracted_images', [])

        # Update the extractor's images if any were extracted
        if extracted_images:
            self.image_extractor.extracted_images = extracted_images
            self.extracted_images = extracted_images

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        yield {
            "response": final_response,
            "title": plan_result.get('title', ''),
            "reading_plan": plan_result.get('reading_plan', []),
            "content_analysis": plan_result.get('content_analysis', {}),
            "extracted_images": extracted_images
        }

    def _generate_quick_scan_summary(self) -> Dict:
        """
        Generate Quick Scan summary with tool support (text output).
        This handles figure extraction and conversational summary.
        """
        logger.info("Generating Quick Scan summary (with tools)")

        # Build system prompt for summary generation
        profile_context = self._build_user_profile_context()
        system_prompt = f"""You are a senior researcher helping users understand research papers.

{QUICK_SCAN_SUMMARY_PROMPT}

{profile_context}

**Response Language**: Always respond in {self.language}.
"""

        # Build contents with PDF
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=self.file.uri, mime_type="application/pdf"),
                    types.Part.from_text(text="Please provide a Quick Scan summary of this paper.")
                ]
            )
        ]

        # Create tools for image extraction
        tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

        # Handle function calls (mainly for image extraction)
        max_iterations = 5
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
                result = self._execute_function(fc)
                function_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response=result)
                )

            contents.append(types.Content(role="user", parts=function_response_parts))

            # Update tools with new images
            tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )

        summary_text = self._extract_text_response(response)
        logger.info(f"Quick Scan summary generated: {len(summary_text)} chars")

        return {
            'summary': summary_text,
            'extracted_images': self.extracted_images
        }

    def _generate_quick_scan_plan(self) -> Dict:
        """
        Generate reading plan (JSON output only, no tools).
        This analyzes paper structure and generates content_analysis + reading_plan.
        """
        import json
        import re

        logger.info("Generating Quick Scan plan (JSON only)")

        # Build system prompt for plan generation
        system_prompt = f"""You are a paper structure analyzer. Your task is to analyze the paper and output a JSON reading plan.

{QUICK_SCAN_PLAN_PROMPT}
"""

        # Build contents with PDF
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=self.file.uri, mime_type="application/pdf"),
                    types.Part.from_text(text="Analyze this paper's structure and generate a reading plan. Output ONLY valid JSON.")
                ]
            )
        ]

        # No tools for plan generation - just JSON output
        config = types.GenerateContentConfig(
            system_instruction=system_prompt
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

        response_text = self._extract_text_response(response)
        logger.info(f"Quick Scan plan response: {len(response_text)} chars")

        # Parse JSON from response
        try:
            text = response_text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            # Find JSON object
            brace_count = 0
            start_idx = -1
            end_idx = -1
            for i, char in enumerate(text):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        end_idx = i + 1
                        break

            if start_idx != -1 and end_idx != -1:
                text = text[start_idx:end_idx]

            data = json.loads(text)
            return {
                'title': data.get('title', ''),
                'content_analysis': data.get('content_analysis', {}),
                'reading_plan': data.get('reading_plan', [])
            }
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Could not parse Quick Scan plan JSON: {e}")
            return {
                'title': '',
                'content_analysis': {},
                'reading_plan': []
            }

    def send_message(self, user_message: str) -> str:
        """
        Send a user message and get agent response.

        Args:
            user_message: User's message/question

        Returns:
            Agent's response text
        """
        response = self._generate_response(user_message)

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
        original_callback = self.status_callback

        def streaming_callback(s):
            self._current_status = s
            if original_callback:
                original_callback(s)

        self.status_callback = streaming_callback
        self._current_status = None

        contents = self._build_contents(user_message)
        full_system_prompt = self._build_system_prompt()
        tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
        config = types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
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
                status_msg = f"Executing: {fc.name}"
                if fc.name == "extract_images":
                    status_msg = "Executing: Extracting figures"
                elif fc.name == "web_search":
                    status_msg = f"Searching web {fc.args.get('query', '')}"
                elif fc.name == "explain_images":
                    status_msg = "Executing: Analyzing figure details"
                elif fc.name == "update_user_profile":
                    status_msg = "Executing: Updating user profile"
                elif fc.name == "generate_animation":
                    concept = fc.args.get('concept', '') if fc.args else ''
                    status_msg = f"Generating animation: {concept[:50]}..." if len(concept) > 50 else f"Generating animation: {concept}"
                elif fc.name == "execute_step":
                    next_stage = fc.args.get('next_stage') if fc.args else None
                    if next_stage:
                        stage_name = get_stage_name(next_stage)
                        status_msg = f"Transitioning to: {stage_name}"
                yield status_msg

                result = self._execute_function(fc)
                function_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response=result)
                )

            contents.append(types.Content(role="user", parts=function_response_parts))

            tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
            config = types.GenerateContentConfig(
                system_instruction=self._build_system_prompt(),
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            yield "Thinking"
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )

        yield "Generating final response"
        result = self._extract_text_response(response)

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        self.status_callback = original_callback

        yield {
            "response": result,
            "extracted_images": self.extracted_images
        }

    def _build_system_prompt(self) -> str:
        """Build full system prompt with user profile, current stage, and extracted images context."""
        profile_context = self._build_user_profile_context()

        base_prompt = META_SYSTEM_PROMPT.format(
            user_profile_context=profile_context,
            language=self.language
        )

        # Add reading plan context if available
        if self.reading_plan:
            plan_str = "\n## Reading Plan for This Paper\n"
            for stage in self.reading_plan:
                stage_id = stage.get('id', '')
                title = stage.get('title', '')
                description = stage.get('description', '')
                plan_str += f"- **{stage_id}**: {title} - {description}\n"
            base_prompt += plan_str

        # Add current stage's detailed instructions
        if self.current_stage_id:
            stage_prompt = get_stage_prompt(self.current_stage_id)
            stage_name = get_stage_name(self.current_stage_id)
            if stage_prompt:
                base_prompt += f"\n\n## Current Stage: {stage_name}\n{stage_prompt}"
                if self.current_stage_id == 'section_deep_dive' and self.current_section:
                    base_prompt += f"\n\n**Currently Exploring Section**: {self.current_section}"

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
        """
        contents = []

        max_history_messages = 20
        history_to_use = self.conversation_history[-max_history_messages:] if len(self.conversation_history) > max_history_messages else self.conversation_history

        for msg in history_to_use:
            role = msg["role"]
            content = msg["content"]

            if len(content) > 2000:
                content = content[:1000] + "... [truncated]" + content[-1000:]

            contents.append(types.Content(
                role=role if role == "user" else "model",
                parts=[types.Part.from_text(text=content)]
            ))

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
        """
        contents = self._build_contents(message)
        full_system_prompt = self._build_system_prompt()
        tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]

        config = types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

        logger.info(f"→ LLM Request ({len(contents)} content parts)")
        if self.status_callback:
            self.status_callback("Thinking")

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

        response, contents = self._handle_function_calls(response, contents, config)

        if self.status_callback:
            self.status_callback("Generating final response")

        result = self._extract_text_response(response)
        logger.info(f"← LLM Response: {len(result)} chars")
        return result

    def _handle_function_calls(self, response, contents: List, config) -> tuple:
        """Handle function calling loop with generate_content."""
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            if not hasattr(response, 'function_calls') or not response.function_calls:
                logger.info(f"✓ Function call loop complete (iteration {iteration})")
                break

            function_calls = response.function_calls
            logger.info(f"⚙ Function Call Round {iteration}: {[fc.name for fc in function_calls]}")

            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            function_response_parts = []
            for idx, fc in enumerate(function_calls):
                logger.info(f"[{idx+1}/{len(function_calls)}] Executing: {fc.name}")

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
                    elif fc.name == "generate_animation":
                        concept = fc.args.get('concept', '') if fc.args else ''
                        status_msg = f"Generating animation: {concept[:50]}..." if len(concept) > 50 else f"Generating animation: {concept}"
                    elif fc.name == "execute_step":
                        next_stage = fc.args.get('next_stage') if fc.args else None
                        if next_stage:
                            stage_name = get_stage_name(next_stage)
                            status_msg = f"Transitioning to: {stage_name}"
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

            contents.append(types.Content(
                role="user",
                parts=function_response_parts
            ))

            full_system_prompt = self._build_system_prompt()
            tools = [types.Tool(function_declarations=create_conversational_tools(self.extracted_images))]
            config = types.GenerateContentConfig(
                system_instruction=full_system_prompt,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )

            logger.info(f"→ Sending function responses to LLM")
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

            elif function_call.name == "generate_animation":
                concept = args.get("concept", "")
                animation_html = args.get("animation_html", "")
                explanation = args.get("explanation", "")
                logger.info(f"🎬 Generating animation for concept: {concept}")

                if not animation_html:
                    return {"success": False, "error": "No animation HTML provided"}

                # Wrap HTML in special markers for frontend detection
                # Using unique markers that won't be affected by markdown/HTML processing
                wrapped_content = f"""{explanation}

<<<ANIMATION_START>>>
{animation_html}
<<<ANIMATION_END>>>"""

                logger.info(f"✓ Animation generated for '{concept}' ({len(animation_html)} chars)")
                return {
                    "success": True,
                    "concept": concept,
                    "content": wrapped_content,
                    "instruction": "Include the content above in your response exactly as provided, preserving all markers and HTML code. The animation will be rendered in an interactive iframe."
                }

            elif function_call.name == "execute_step":
                previous_stage = args.get("previous_stage", self.current_stage_id or 'quick_scan')
                next_stage = args.get("next_stage", 'quick_scan')
                mode = args.get("mode", "transition")
                reason = args.get("reason", "")
                section_name = args.get("section_name", None)

                logger.info(f"📖 Execute step: '{previous_stage}' -> '{next_stage}' (mode={mode}): {reason}")

                stage_name = get_stage_name(next_stage)
                stage_prompt = get_stage_prompt(next_stage)

                self.current_stage_id = next_stage

                if next_stage == 'section_deep_dive' and section_name:
                    self.current_section = section_name
                    logger.info(f"📖 Exploring section: {section_name}")

                if mode == "qa":
                    logger.info(f"✓ Q&A mode in stage '{next_stage}' ({stage_name})")
                    return {
                        "success": True,
                        "mode": "qa",
                        "previous_stage": previous_stage,
                        "next_stage": next_stage,
                        "stage_name": stage_name,
                        "reason": reason,
                        "action_required": "Answer the user's question directly. Use the current stage context but do NOT regenerate the full stage content.",
                        "stage_context": stage_prompt
                    }
                else:
                    logger.info(f"✓ Transitioned from '{previous_stage}' to '{next_stage}' ({stage_name})")
                    result = {
                        "success": True,
                        "mode": "transition",
                        "previous_stage": previous_stage,
                        "next_stage": next_stage,
                        "stage_name": stage_name,
                        "reason": reason,
                        "action_required": f"IMPORTANT: You MUST now immediately generate the FULL {stage_name} content. Do NOT just acknowledge - perform the complete stage analysis now.",
                        "stage_instructions": stage_prompt
                    }
                    if section_name:
                        result["section_name"] = section_name
                        result["action_required"] += f" Focus on the section: {section_name}"
                    return result

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

    def set_reading_plan(self, reading_plan: list) -> None:
        """
        Set the dynamic reading plan from Quick Scan response.

        Args:
            reading_plan: List of stage definitions from Quick Scan
        """
        self.reading_plan = reading_plan or []
        logger.info(f"Reading plan set with {len(self.reading_plan)} stages")

    def get_reading_plan(self) -> list:
        """Get the current reading plan."""
        return self.reading_plan

    def set_current_stage(self, stage_id: str, section_name: str = None) -> None:
        """
        Set the current stage ID.

        Args:
            stage_id: Stage identifier (e.g., "quick_scan", "methodology")
            section_name: Optional section name for section_deep_dive
        """
        self.current_stage_id = stage_id
        if section_name:
            self.current_section = section_name
        logger.info(f"Current stage set to '{stage_id}'" + (f" (section: {section_name})" if section_name else ""))

    def get_current_stage_id(self) -> str:
        """Get the current stage ID."""
        return self.current_stage_id
