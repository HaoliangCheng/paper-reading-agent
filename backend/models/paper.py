from dataclasses import dataclass, field
from typing import List


@dataclass
class PaperAnalysis:
    """Stores extracted figures and metadata for a paper"""
    all_figures: List[dict] = field(default_factory=list)
    # Each dict: {title, bbox, type, confidence, page, image_path, image_hash}
