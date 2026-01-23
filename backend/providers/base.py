"""Abstract base classes for providers"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image as PILImage


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers (Gemini, OpenAI, etc.)"""

    @abstractmethod
    def upload_file(self, file_path: str) -> Any:
        """Upload a file to the LLM provider and return file object"""
        pass

    @abstractmethod
    def get_file(self, file_name: str) -> Any:
        """Get a previously uploaded file by name"""
        pass

    @abstractmethod
    def create_chat(self) -> Any:
        """Create a new chat session for multi-turn conversation"""
        pass

    @abstractmethod
    def generate_content(self, contents: List, config: Optional[Dict] = None) -> str:
        """Generate content from the LLM"""
        pass

    @abstractmethod
    def analyze_paper_metadata(self, file) -> Tuple[str, List[int]]:
        """
        Extract paper title and identify figure pages in one call.

        Returns:
            Tuple of (paper_title, list_of_page_numbers_with_figures)
        """
        pass

    @abstractmethod
    def detect_figure_bboxes_batch(self, page_images: List[Tuple[PILImage.Image, int]]) -> List[dict]:
        """
        Batch detect figure bounding boxes from multiple pages

        Args:
            page_images: List of (PIL_Image, page_num) tuples

        Returns:
            List of detections with bbox coordinates
        """
        pass

    @abstractmethod
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
            prompt: Step-specific prompt
            figure_tool_description: Description for the display_selected_images tool

        Returns:
            Tuple of (response_text, displayed_images)
        """
        pass

    @abstractmethod
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
            prompt: Step-specific prompt

        Returns:
            Tuple of (response_text, grounding_sources)
        """
        pass

    @abstractmethod
    def chat_send_message(self, chat, message: str) -> str:
        """Send a message in an existing chat session"""
        pass

    @abstractmethod
    def answer_question(self, file_uri: str, mime_type: str, question: str, language: str) -> str:
        """Answer a question about the paper"""
        pass
