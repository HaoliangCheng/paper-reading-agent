"""Gemini LLM Provider implementation"""

import io
import os
import time
import json
import re
import logging
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image as PILImage
from google import genai
from google.genai import types
from dotenv import load_dotenv

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

# Ensure .env is loaded
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider implementation with chat support"""

    def __init__(self, model_id: str = "gemini-3-flash-preview"):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_id

    def create_chat(self) -> Any:
        """Create a new chat session for multi-turn conversation"""
        return self.client.chats.create(model=self.model_id)

    def upload_file(self, file_path: str, timeout_seconds: int = 120) -> Any:
        """
        Upload PDF to Gemini File API and wait for processing.

        Args:
            file_path: Path to the file to upload
            timeout_seconds: Maximum time to wait for upload and processing (default: 120 seconds / 2 minutes)

        Returns:
            Gemini file object

        Raises:
            TimeoutError: If upload or processing takes longer than timeout_seconds
            Exception: If Gemini file processing fails
        """
        logger.info(f"Uploading file to Gemini: {file_path}")
        start_time = time.time()

        # Wrap the upload call with a timeout using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.client.files.upload, file=file_path)
            try:
                file = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                logger.error(f"File upload timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"File upload timed out after {timeout_seconds} seconds. Please try again with a smaller file or check your network connection.")

        elapsed_time = time.time() - start_time
        logger.info(f"File upload and processing completed in {elapsed_time:.1f}s")
        return file

    def get_file(self, file_name: str) -> Any:
        """Get a previously uploaded file by name"""
        return self.client.files.get(name=file_name)

    def extract_paper_title(self, file) -> str:
        """
        Extract paper title from PDF.

        Args:
            file: Gemini file object

        Returns:
            Paper title string
        """
        prompt = """Extract the title of this paper.

**Rules:**
- Extract the main title from the first page
- Include subtitle if present (separated by colon)
- Do NOT include author names, affiliations, or dates

**Output Format:**
Return ONLY the title text, nothing else."""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[file, prompt]
            )

            title = response.text.strip().strip('"\'')
            return title

        except Exception as e:
            logger.error(f"Error extracting paper title: {e}", exc_info=True)
            return ""

    def generate_content(self, contents: List, config: Optional[Dict] = None) -> str:
        """Generate content from Gemini"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )
        return response.text

    def analyze_paper_metadata(self, file) -> Tuple[str, List[int]]:
        """
        Extract paper title and identify figure pages in a single LLM call.

        Returns:
            Tuple of (paper_title, list_of_page_numbers_with_figures)
        """
        prompt = """Analyze this PDF and extract:
1. The paper title
2. Which pages contain figures/diagrams

**Task 1 - Paper Title**:
- Extract the main title from the first page
- Include subtitle if present (separated by colon)
- Do NOT include author names, affiliations, or dates

**Task 2 - Figure Pages**:
INCLUDE pages with:
- Architecture diagrams, system diagrams, flowcharts
- Charts, graphs, plots (line charts, bar charts, scatter plots)
- Algorithm visualizations, conceptual illustrations
- Example images showing results (photos, screenshots, renderings)

EXCLUDE pages with:
- Only text and math equations
- Only tables (data tables, comparison tables)
- Title page, references, bibliography
- Pages with just small icons, logos, or decorative elements

**Output Format (JSON only):**
{
  "title": "The Paper Title Here",
  "pages_with_figures": [1, 3, 5, 7, 8]
}

Respond ONLY with valid JSON."""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[file, prompt]
            )

            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            result = json.loads(text)
            title = result.get("title", "").strip().strip('"\'')
            pages = result.get("pages_with_figures", [])

            return title, pages

        except Exception as e:
            logger.error(f"Error analyzing paper metadata: {e}", exc_info=True)
            return "", []

    def detect_figure_bboxes_batch(self, page_images: List[Tuple[PILImage.Image, int]]) -> List[dict]:
        """
        Batch detect figure bounding boxes from multiple pages in ONE LLM call

        Args:
            page_images: List of (PIL_Image, page_num) tuples

        Returns:
            List of detections with bbox coordinates
        """
        if not page_images:
            return []

        # Prepare all images and create page mapping
        image_parts = []
        page_mapping = []  # Maps image index to page number

        for idx, (image, page_num) in enumerate(page_images):
            # Convert PIL Image to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            # Add to parts
            image_parts.append(
                types.Part.from_bytes(data=img_bytes, mime_type='image/png')
            )
            page_mapping.append(page_num)

        # Create image list for prompt
        image_list = "\n".join([f"- Image {i}: Page {page_num}" for i, page_num in enumerate(page_mapping)])

        prompt = f"""Analyze these {len(page_images)} images and detect all figures, diagrams, charts, and visualizations.

**Images provided:**
{image_list}

**Coordinate System:**
- Origin (0, 0) = top-left corner
- (1, 1) = bottom-right corner
- Format: [x_min, y_min, x_max, y_max] in 0-1 normalized scale

**Figure Types to DETECT:**
- diagram: Architecture diagrams, flow diagrams, conceptual drawings, system diagrams
- chart: Line graphs, bar charts, scatter plots, performance graphs, histograms
- photo: Photographs, example images, screenshots, renderings
- illustration: Algorithm visualizations, conceptual illustrations, drawings

**EXCLUDE (do NOT detect):**
- Tables (data tables, comparison tables, numerical tables)
- Mathematical equations (standalone equations, equation blocks)
- Page headers, footers, page numbers
- Figure captions and labels (detect only the visual content itself)
- Small icons, logos, or decorative elements

**Important Rules:**
1. **Extract ONE image per complete figure** - If a figure contains multiple subfigures (a), (b), (c), provide ONE bounding box that encompasses the entire figure, NOT separate boxes for each subfigure
2. Provide tight bounding boxes around each complete figure
3. Focus on extracting meaningful visual content only (diagrams, charts, photos)
4. Do NOT extract tables or equations
5. **Include image_index** to indicate which image (0-indexed) the detection belongs to

**Output Format (VALID JSON ONLY):**
{{
  "detections": [
    {{
      "image_index": 0,
      "title": "Clear, descriptive title for this image (serves as the figure caption)",
      "bbox": [0.05, 0.1, 0.95, 0.5],
      "type": "diagram",
      "confidence": 0.95
    }},
    {{
      "image_index": 2,
      "title": "Another figure title",
      "bbox": [0.1, 0.2, 0.9, 0.8],
      "type": "chart",
      "confidence": 0.92
    }}
  ]
}}

Respond ONLY with valid JSON, no additional text."""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[*image_parts, prompt]
            )

            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            result = json.loads(text)
            detections = result.get("detections", [])

            # Map image_index to actual page numbers
            for det in detections:
                img_idx = det.get("image_index", 0)
                if 0 <= img_idx < len(page_mapping):
                    det["page"] = page_mapping[img_idx]
                else:
                    logger.warning(f"Invalid image_index {img_idx}, using first page")
                    det["page"] = page_mapping[0] if page_mapping else 1

                # Remove image_index from final output
                det.pop("image_index", None)

            return detections

        except Exception as e:
            logger.error(f"Batch bbox detection failed: {e}", exc_info=True)
            return []

    def generate_summary_with_figures(
        self,
        file,
        image_parts: List,
        all_figures: List[dict],
        language: str
    ) -> Tuple[str, List[Dict]]:
        """Generate summary using title, abstract, and figures with function calling"""
        figure_descriptions = [f"Image {idx}: {fig['title']}" for idx, fig in enumerate(all_figures)]

        prompt = f"""Based on this paper's title, abstract, and the provided related figures, provide a concise summary in {language}.

Requirements:
1. 2-3 sentences total.
2. Answer: What problem? What solution? What results?
3. Focus on high-level understanding (no technical details).
4. After viewing {len(image_parts)} images, use the display_selected_images function to display relevant figures that help explain the key high-level idea of the paper.
5. After calling the function, incorporate the returned image paths into your summary using markdown syntax.

Available Images:
{chr(10).join(figure_descriptions)}

After you receive the image locations from display_selected_images, respond with ONLY valid JSON in this exact format:
{{
    "Title": "Paper title here",
    "summary": "Your 2-3 sentence summary here with markdown image references like ![caption](image_path.png)"
}}

IMPORTANT NOTE: 
The image shows after a ',' or '.' or '!' or '?', like 'System Architecture, ![System Architecture](image_path.png)'.
"""

        display_images_declaration = types.FunctionDeclaration(
            name="display_selected_images",
            description="Display selected images from the paper that help understand the high level idea.",
            parameters={
                "type": "object",
                "properties": {
                    "image_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "0-indexed image indices to display"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Why these images are important"
                    }
                },
                "required": ["image_indices", "reasoning"]
            }
        )

        tools = types.Tool(function_declarations=[display_images_declaration])
        config = types.GenerateContentConfig(tools=[tools])

        def get_image_locations(image_indices: List[int]) -> dict:
            """Helper to map indices to paths for Gemini function response"""
            image_paths = []
            for idx in image_indices:
                if idx < len(all_figures):
                    fig = all_figures[idx]
                    # Use relative path for frontend display
                    path = fig.get("image_path_relative", fig.get("image_path", ""))
                    image_paths.append({
                        "index": idx,
                        "path": path,
                        "title": fig["title"]
                    })
            return {"success": True, "images": image_paths}

        try:
            # Initial request
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[file, *image_parts, prompt],
                config=config
            )

            displayed_images = []
            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                if not response.candidates or not response.candidates[0].content.parts:
                    break

                parts = response.candidates[0].content.parts
                function_call_found = False

                for part in parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_call_found = True
        
                        if function_call.name == "display_selected_images":
                            args = dict(function_call.args)
                            indices = args.get('image_indices', [])
                            reasoning = args.get('reasoning', 'Not specified')

                            result = get_image_locations(indices)
                            displayed_images = result.get("images", [])
                            
                            # Build conversation preserving the original model response
                            response = self.client.models.generate_content(
                                model=self.model_id,
                                contents=[
                                    file, *image_parts, prompt,
                                    response.candidates[0].content,  # Preserves thought_signature automatically
                                    types.Content(parts=[
                                        types.Part.from_function_response(
                                            name="display_selected_images",
                                            response=result
                                        )
                                    ])
                                ],
                                config=config
                            )
                        break

                if not function_call_found:
                    # Look for the final text response
                    text_parts = []
                    for part in parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)

                    if text_parts:
                        full_text = ' '.join(text_parts).strip()
                        # Try to extract JSON from response
                        try:
                            json_text = re.sub(r'^```json\s*', '', full_text)
                            json_text = re.sub(r'\s*```$', '', json_text)
                            json.loads(json_text)
                            return json_text, displayed_images
                        except:
                            return json.dumps({"Title": "Paper", "summary": full_text}), displayed_images
                    break

            # Fallback
            final_text = response.text if hasattr(response, 'text') else str(response)
            try:
                json_text = re.sub(r'^```json\s*', '', final_text)
                json_text = re.sub(r'\s*```$', '', json_text)
                json.loads(json_text)
                return json_text, displayed_images
            except:
                return json.dumps({"Title": "Paper", "summary": final_text}), displayed_images

        except Exception as e:
            logger.error(f"Error in generate_summary_with_figures: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return json.dumps({"Title": "Error", "summary": f"Error generating summary: {str(e)}"}), []

    def answer_question(self, file_uri: str, mime_type: str, question: str, language: str) -> str:
        """Answer a question using the Gemini file context"""
        prompt = f"Based on the attached paper, answer this question in {language}: {question}"
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ]
            )
            return response.text
        except Exception as e:
            return f"Error answering question: {str(e)}"

    def chat_send_message(self, chat, message: str) -> str:
        """Send a message in an existing chat session"""
        try:
            response = chat.send_message(message)
            return response.text.strip() if response.text else ""
        except Exception as e:
            return f"Error: {str(e)}"

    def _prepare_figure_parts(self, all_figures: List[dict]) -> Tuple[List, List[str]]:
        """Prepare image parts and descriptions from figures"""
        image_parts = []
        figure_descriptions = []

        for idx, fig in enumerate(all_figures):
            try:
                img = PILImage.open(fig["image_path"])
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_bytes = img_buffer.getvalue()

                image_parts.append(
                    types.Part.from_bytes(data=img_bytes, mime_type='image/png')
                )
                figure_descriptions.append(f"Image {idx}: {fig['title']}")
            except Exception as e:
                logger.warning(f"Could not load image {fig.get('image_path')}: {e}")

        return image_parts, figure_descriptions

    def generate_step_with_figures(
        self,
        chat,
        file,
        all_figures: List[dict],
        prompt: str,
        figure_tool_description: str
    ) -> Tuple[str, List[Dict]]:
        """
        Generate step content with figure selection using chat and function calling

        Args:
            chat: Chat session object
            file: Uploaded file object
            all_figures: List of figure metadata
            prompt: Step-specific prompt (should include {figure_list} placeholder)
            figure_tool_description: Description for the display_selected_images tool

        Returns:
            Tuple of (response_text, displayed_images)
        """
        # If no figures, just send the prompt
        if not all_figures:
            response = chat.send_message([file, prompt.replace("{figure_list}", "No figures available.")])
            return response.text.strip() if response.text else "", []

        # Prepare image parts and descriptions
        image_parts, figure_descriptions = self._prepare_figure_parts(all_figures)
        figure_list = "\n".join(figure_descriptions)

        # Helper function for image locations
        def get_image_locations(image_indices: List[int]) -> dict:
            image_paths = []
            for idx in image_indices:
                if idx < len(all_figures):
                    fig = all_figures[idx]
                    image_paths.append({
                        "index": idx,
                        "path": fig.get("image_path_relative", fig.get("image_path", "")),
                        "title": fig["title"]
                    })
            print(f"   Agent selected {len(image_indices)} images: {image_indices}")
            return {"success": True, "images": image_paths}

        # Create function declaration
        display_images_declaration = types.FunctionDeclaration(
            name="display_selected_images",
            description=figure_tool_description,
            parameters={
                "type": "object",
                "properties": {
                    "image_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of 0-indexed image positions to display"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why these images are important"
                    }
                },
                "required": ["image_indices", "reasoning"]
            }
        )

        tools = types.Tool(function_declarations=[display_images_declaration])
        config = types.GenerateContentConfig(tools=[tools])

        # Format prompt with figure list
        formatted_prompt = prompt.replace("{figure_list}", figure_list)

        # Send message through chat
        response = chat.send_message(
            [file, *image_parts, formatted_prompt],
            config=config
        )

        displayed_images = []
        max_iterations = 5

        # Handle function calling loop
        for _ in range(max_iterations):
            if not response.candidates or not response.candidates[0].content.parts:
                break

            parts = response.candidates[0].content.parts
            function_call_found = False

            for part in parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_call_found = True

                    if function_call.name == "display_selected_images":
                        args_dict = dict(function_call.args)
                        image_indices = args_dict.get('image_indices', [])
                        reasoning = args_dict.get('reasoning', 'Not specified')

                        if not isinstance(image_indices, list):
                            image_indices = list(image_indices)

                        result = get_image_locations(image_indices)
                        displayed_images = result.get("images", [])

                        # Send function result - use Part directly
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name="display_selected_images",
                                response=result
                            ),
                            config=config
                        )
                    break

            if function_call_found:
                continue

            # Look for text response
            text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
            if text_parts:
                return ' '.join(text_parts).strip(), displayed_images
            break

        # Fallback
        text_parts = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
        return ' '.join(text_parts).strip() if text_parts else "", displayed_images

    def web_search(self, query: str, language: str = "English") -> dict:
        """
        Perform a web search using Google Search grounding.

        Args:
            query: Search query
            language: Response language

        Returns:
            dict with 'answer' and 'sources'
        """
        try:
            prompt = f"""Search for: {query}

Provide a comprehensive answer based on the search results.
Respond in {language}.

Include relevant facts, recent developments, and cite your sources."""

            # Use Google Search grounding (without function calling)
            # Reference: https://ai.google.dev/gemini-api/docs/google-search
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"]
            )

            logger.info(f"Web search query: {query}")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )

            answer = response.text.strip() if response.text else "No results found."

            # Extract grounding sources from grounding_metadata
            # The metadata contains grounding_chunks (web sources) and grounding_supports (text-to-source links)
            sources = []
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata

                    # Extract web sources from grounding_chunks
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    'title': getattr(chunk.web, 'title', 'Unknown'),
                                    'uri': getattr(chunk.web, 'uri', '')
                                })

                    # Log search queries if available
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        logger.debug(f"Search queries: {metadata.web_search_queries}")

            logger.info(f"Web search completed: {len(sources)} sources found")
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "instruction": "Use this information to answer the user's question. Cite the sources when relevant."
            }

        except Exception as e:
            logger.error(f"Web search failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "answer": f"Search failed: {str(e)}",
                "sources": []
            }

    def explain_figure(self, image_path: str, question: str, language: str = "English") -> str:
        """
        Explain a figure/image based on user's question.

        Args:
            image_path: Path to the image file
            question: User's question about the image
            language: Language for the response

        Returns:
            LLM response explaining the figure
        """
        try:
            # Load the image
            img = PILImage.open(image_path)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')

            prompt = f"""Analyze this figure/image and answer the following question in {language}.

Question: {question}

Please provide a clear and detailed explanation based on what you see in the image.
If the image contains charts, diagrams, or visualizations, describe the key elements and their relationships.
If there are labels, axes, or annotations, explain what they represent."""

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[image_part, prompt]
            )

            return response.text.strip() if response.text else "Unable to analyze the image."

        except FileNotFoundError:
            return f"Error: Image file not found at {image_path}"
        except Exception as e:
            return f"Error analyzing figure: {str(e)}"

    def generate_step_with_search(
        self,
        chat,
        file,
        all_figures: List[dict],
        prompt: str
    ) -> Tuple[str, List[Dict]]:
        """
        Generate step content with Google Search grounding

        Args:
            chat: Chat session object
            file: Uploaded file object
            all_figures: List of figure metadata
            prompt: Step-specific prompt (should include {figure_list} placeholder)

        Returns:
            Tuple of (response_text, grounding_sources)
        """
        # Prepare figure list
        figure_list = "No figures available."
        if all_figures:
            figure_descriptions = [f"Image {idx}: {fig['title']}" for idx, fig in enumerate(all_figures)]
            figure_list = "\n".join(figure_descriptions)

        # Format prompt
        formatted_prompt = prompt.replace("{figure_list}", figure_list)

        # Setup Google Search grounding
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

        try:
            response = chat.send_message(formatted_prompt, config=config)
            analysis_text = response.text.strip() if response.text else ""

            # Extract grounding sources
            grounding_sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata

                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                grounding_sources.append({
                                    'title': chunk.web.title if hasattr(chunk.web, 'title') else 'Unknown',
                                    'uri': chunk.web.uri if hasattr(chunk.web, 'uri') else ''
                                })

            return analysis_text, grounding_sources

        except Exception as e:
            logger.error(f"Google Search grounding failed: {e}")
            # Fallback without search
            try:
                response = chat.send_message(formatted_prompt.replace("Use Google Search", "Analyze"))
                return response.text.strip() if response.text else "", []
            except:
                return "Critical analysis generation failed", []
