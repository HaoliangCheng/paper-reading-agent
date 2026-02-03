"""On-Demand Image Extractor for Design 4"""

import os
import io
import re
import json
import logging
from typing import List, Dict, Any, Tuple
from PIL import Image as PILImage
import fitz  # PyMuPDF
from google.genai import types

logger = logging.getLogger(__name__)


class OnDemandImageExtractor:
    """
    Extracts images on-demand based on page numbers and descriptions.

    Features:
    - Batch extraction for efficiency
    - Tracks all extracted images
    - Uses LLM to detect figure bounding boxes
    - Design 2 naming convention: {pdf_stem}_page{page}_fig{idx}_{type}.png
    """

    def __init__(self, pdf_path: str, paper_folder: str, llm_client, model_id: str):
        """
        Initialize the on-demand extractor.

        Args:
            pdf_path: Path to the PDF file
            paper_folder: Folder to save extracted images
            llm_client: Gemini client for figure detection
            model_id: Model ID for LLM calls
        """
        self.pdf_path = pdf_path
        self.paper_folder = paper_folder
        self.pdf_stem = os.path.splitext(os.path.basename(pdf_path))[0]
        self.client = llm_client
        self.model_id = model_id
        self.extraction_count = 0
        self.extracted_images: List[Dict] = []

        os.makedirs(paper_folder, exist_ok=True)

    def extract_images_batch(self, images_to_extract: List[Dict]) -> Dict:
        """
        Extract multiple figures in a single batch call.

        Args:
            images_to_extract: List of dicts with 'page_number' and 'description'

        Returns:
            dict with 'success', 'extracted_images', and 'message'
        """
        if not images_to_extract:
            logger.warning("⚠️ No images requested for extraction")
            return {
                "success": False,
                "extracted_images": [],
                "message": "No images requested for extraction"
            }

        logger.info(f"🔄 Starting batch extraction: {len(images_to_extract)} images")

        try:
            # Step 1: Group requests by page
            page_requests = {}
            for req in images_to_extract:
                page_num = req.get("page_number", 1)
                if page_num not in page_requests:
                    page_requests[page_num] = []
                page_requests[page_num].append(req.get("description", "figure"))

            logger.info(f"📄 Pages: {list(page_requests.keys())}")

            # Step 2: Render pages
            logger.info(f"🖨️ Rendering {len(page_requests)} page(s)...")
            doc = fitz.open(self.pdf_path)
            page_images = {}

            for page_num in page_requests.keys():
                if page_num < 1 or page_num > len(doc):
                    logger.warning(f"⚠️ Invalid page {page_num} (PDF has {len(doc)} pages)")
                    continue

                try:
                    page = doc[page_num - 1]
                    mat = fitz.Matrix(2.0, 2.0)
                    pix = page.get_pixmap(matrix=mat)
                    page_images[page_num] = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                except Exception as e:
                    logger.error(f"✗ Failed to render page {page_num}: {e}")

            doc.close()
            logger.info(f"✓ Rendered {len(page_images)}/{len(page_requests)} page(s)")

            if not page_images:
                logger.error("✗ No valid pages rendered")
                return {
                    "success": False,
                    "extracted_images": [],
                    "message": "No valid pages to render"
                }

            # Step 3: Detect figures using LLM
            logger.info(f"🤖 Detecting figures with LLM...")
            all_detections = self._detect_figures_batch(page_images, page_requests)

            if not all_detections:
                logger.warning("⚠️ No figures detected by LLM")
                return {
                    "success": False,
                    "extracted_images": [],
                    "message": "Could not detect any figures matching the descriptions"
                }

            logger.info(f"✓ Detected {len(all_detections)} figure(s)")

            # Step 4: Crop and save figures
            logger.info(f"✂️ Cropping and saving {len(all_detections)} figure(s)...")
            extracted = self._crop_and_save_batch(page_images, all_detections)

            if extracted:
                # Build markdown for response
                markdown_images = [
                    f"![{img['title']}]({img['path_relative']})"
                    for img in extracted
                ]
                logger.info(f"✅ Extraction complete: {len(extracted)} figure(s) saved")
                return {
                    "success": True,
                    "extracted_images": extracted,
                    "markdown_images": markdown_images,
                    "message": f"Successfully extracted {len(extracted)} figures."
                }
            else:
                logger.error("✗ Failed to save any figures")
                return {
                    "success": False,
                    "extracted_images": [],
                    "message": "Failed to crop any figures"
                }

        except Exception as e:
            logger.error(f"✗ Batch extraction error: {e}", exc_info=True)
            return {
                "success": False,
                "extracted_images": [],
                "message": f"Error extracting images: {str(e)}"
            }

    def _detect_figures_batch(self, page_images: Dict[int, PILImage.Image],
                               page_requests: Dict[int, List[str]]) -> List[Dict]:
        """
        Use LLM to detect figure bounding boxes in batch.
        """
        content_parts = []
        page_mapping = []
        valid_pages = list(page_images.keys())

        for page_num, image in sorted(page_images.items()):
            descriptions = page_requests.get(page_num, [])

            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type='image/png'))
            page_mapping.append({
                "page_num": page_num,
                "descriptions": descriptions
            })

        # Build prompt with explicit page numbers
        prompt = f"""Analyze these PDF page images and detect the figures/diagrams.

IMPORTANT: Only use these page numbers in your response: {valid_pages}

For each page, find figures matching these descriptions:
"""
        for pm in page_mapping:
            prompt += f"\nPage {pm['page_num']}: {', '.join(pm['descriptions'])}"

        prompt += f"""

**Output Format (JSON only):**
{{
  "detections": [
    {{
      "page": <must be one of {valid_pages}>,
      "title": "Figure X: Description",
      "type": "diagram",
      "bbox": [x_min, y_min, x_max, y_max],
      "matched_description": "description from request"
    }}
  ]
}}

Coordinates: Provide bbox as [ymin, xmin, ymax, xmax] normalized to 1000.
- Example: [284, 506, 680, 881] means top=28.4%, left=50.6%, bottom=68%, right=88.1%
Types: diagram, chart, table, graph, photo, equation

Return ONLY valid JSON."""

        content_parts.append(prompt)

        try:
            logger.info(f"→ LLM Request: detect figures on {len(page_images)} pages")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=content_parts
            )

            # Handle None or empty response
            if not response or not response.text:
                logger.error("✗ Empty LLM response")
                return []

            logger.info(f"← LLM Response: {len(response.text)} chars")

            # Parse JSON response
            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            try:
                result = json.loads(text)
                detections = result.get("detections", [])
                logger.info(f"✓ Parsed {len(detections)} detection(s)")
            except json.JSONDecodeError as e:
                logger.error(f"✗ JSON parse error: {e}")
                logger.error(f"Response: {text[:500]}...")
                return []

            # Filter detections to only include valid pages
            valid_detections = [d for d in detections if d.get("page") in valid_pages]
            if len(valid_detections) < len(detections):
                filtered_count = len(detections) - len(valid_detections)
                logger.warning(f"⚠️ Filtered {filtered_count} invalid detection(s)")

            logger.info(f"✓ {len(valid_detections)} valid detection(s)")

            return valid_detections

        except Exception as e:
            logger.error(f"✗ Figure detection error: {e}", exc_info=True)
            return []

    def _crop_and_save_batch(self, page_images: Dict[int, PILImage.Image],
                              detections: List[Dict]) -> List[Dict]:
        """
        Crop and save all detected figures.
        Handles multiple bbox formats:
        - [ymin, xmin, ymax, xmax] normalized to 1000 (Gemini default)
        - [x_min, y_min, x_max, y_max] normalized to 0-1
        - [x_min, y_min, x_max, y_max] pixel coordinates
        """
        extracted = []
        padding = 10

        for idx, det in enumerate(detections):
            try:
                page_num = det.get("page")
                title = det.get("title", f"Figure {idx+1}")
                logger.info(f"[{idx+1}/{len(detections)}] {title}")
                
                if page_num not in page_images:
                    logger.warning(f"⚠️ Page {page_num} not available")
                    continue

                image = page_images[page_num]
                img_width, img_height = image.size
                bbox = det.get("bbox", [0, 0, 1000, 1000])

                # Validate bbox
                if not bbox or len(bbox) != 4:
                    logger.warning(f"⚠️ Invalid bbox: {bbox}")
                    continue

                # Detect bbox format and convert to pixel coordinates
                max_val = max(bbox)

                if max_val <= 1:
                    # Format: normalized 0-1, order [x_min, y_min, x_max, y_max]
                    x_min = int(bbox[0] * img_width)
                    y_min = int(bbox[1] * img_height)
                    x_max = int(bbox[2] * img_width)
                    y_max = int(bbox[3] * img_height)
                elif max_val <= 1000:
                    # Format: normalized to 1000, order [ymin, xmin, ymax, xmax]
                    ymin, xmin, ymax, xmax = bbox
                    x_min = int((xmin / 1000.0) * img_width)
                    y_min = int((ymin / 1000.0) * img_height)
                    x_max = int((xmax / 1000.0) * img_width)
                    y_max = int((ymax / 1000.0) * img_height)
                else:
                    # Format: pixel coordinates, order [x_min, y_min, x_max, y_max]
                    x_min = int(bbox[0])
                    y_min = int(bbox[1])
                    x_max = int(bbox[2])
                    y_max = int(bbox[3])

                # Apply padding and bounds checking
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(img_width, x_max + padding)
                y_max = min(img_height, y_max + padding)

                # Check valid crop region
                if x_max <= x_min or y_max <= y_min:
                    logger.warning(f"⚠️ Invalid crop region: ({x_min},{y_min})-({x_max},{y_max})")
                    continue

                # Crop image
                cropped = image.crop((x_min, y_min, x_max, y_max))

                # Save file
                fig_type = det.get("type", "figure")
                filename = f"{self.pdf_stem}_page{page_num}_fig{self.extraction_count + 1}_{fig_type}.png"
                filepath = os.path.join(self.paper_folder, filename)

                try:
                    cropped.save(filepath, format="PNG")
                except Exception as e:
                    logger.error(f"✗ Save failed: {e}")
                    continue

                # Verify file was saved successfully
                if not os.path.exists(filepath):
                    logger.error(f"✗ File not found: {filename}")
                    continue
                    
                file_size = os.path.getsize(filepath)
                if file_size == 0:
                    logger.error(f"✗ Empty file: {filename}")
                    os.remove(filepath)
                    continue

                logger.info(f"✓ {filename} ({file_size} bytes)")

                folder_name = os.path.basename(self.paper_folder)
                relative_path = f"uploads/{folder_name}/{filename}"

                self.extraction_count += 1

                fig_data = {
                    "page": page_num,
                    "title": det.get("title", f"Figure {self.extraction_count}"),
                    "type": fig_type,
                    "description": det.get("matched_description", ""),
                    "path": filepath,
                    "path_relative": relative_path
                }

                extracted.append(fig_data)
                self.extracted_images.append(fig_data)

            except Exception as e:
                logger.error(f"✗ Error processing [{idx+1}]: {e}", exc_info=True)
                continue

        logger.info(f"✓ Saved {len(extracted)}/{len(detections)} figure(s)")
        return extracted

    def get_extracted_images(self) -> List[Dict]:
        """Get list of all extracted images."""
        return self.extracted_images
