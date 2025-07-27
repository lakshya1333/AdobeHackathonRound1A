"""
Data Structures Module for Offline PDF Heading Extraction

This module defines the core data structures used throughout the PDF heading
extraction system. All structures are designed to be lightweight and contain
comprehensive metadata for analysis.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TextBlock:
    """
    Represents a text block extracted from a PDF with comprehensive metadata.
    
    This class stores all relevant information about a text block including
    its content, formatting, spatial properties, and analysis results.
    """
    # Core text properties
    text: str
    font_size: float
    font_name: str
    font_flags: int
    bbox: List[float]  # [x0, y0, x1, y1]
    page: int
    
    # Text analysis properties
    line_count: int = 1
    word_count: int = 0
    char_count: int = 0
    sentence_count: int = 1
    avg_word_length: float = 0
    
    # Font and formatting properties
    is_bold: bool = False
    is_italic: bool = False
    color: Tuple[float, float, float] = (0, 0, 0)
    
    # Spatial properties
    spacing_before: float = 0
    spacing_after: float = 0
    indentation: float = 0
    
    # Content analysis ratios
    caps_ratio: float = 0
    numeric_ratio: float = 0
    punctuation_ratio: float = 0
    special_char_ratio: float = 0
    stopword_ratio: float = 0
    
    # Classification results
    heading_confidence: float = 0.0
    
    def __post_init__(self):
        """Initialize computed properties after object creation."""
        if self.text:
            self.char_count = len(self.text)
            words = self.text.split()
            self.word_count = len(words)
            if words:
                self.avg_word_length = sum(len(word) for word in words) / len(words)
