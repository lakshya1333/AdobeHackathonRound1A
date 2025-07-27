#!/usr/bin/env python3
"""
Generic PDF Heading Extractor
A robust, document-agnostic PDF heading extraction system that works across different PDF formats and layouts.
"""

import json
import logging
import re
import statistics
import time
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter

import fitz  # PyMuPDF

from data_structures import TextBlock

def setup_logging():
    """Simple logging setup"""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

class GenericPDFHeadingExtractor:
    """Generic PDF heading extractor that works across different document types and formats"""

    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the generic extractor.

        Args:
            confidence_threshold: Minimum confidence score for heading detection (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold

        # Generic patterns for heading detection (not document-specific)
        self.heading_indicators = {
            'numbered_section': r'^\d+\.(\d+\.)*\s+',  # "1.", "1.1.", "1.1.1."
            'numbered_list': r'^\d+\)\s+',  # "1) Item"
            'lettered_list': r'^[A-Z]\)\s+',  # "A) Item"
            'bullet_point': r'^[•·▪▫◦‣⁃]\s+',  # Various bullet characters
            'title_case_colon': r'^[A-Z][a-z].*:$',  # "Title Case:"
            'all_caps': r'^[A-Z\s\d\-_]+$',  # "ALL CAPS TEXT"
            'mixed_case_short': r'^[A-Z][a-zA-Z\s]{2,50}$',  # Short title case text
        }

        # Common heading keywords (language-agnostic where possible)
        self.heading_keywords = {
            'structural': ['table of contents', 'contents', 'index', 'references', 'bibliography',
                          'appendix', 'glossary', 'acknowledgements', 'preface', 'foreword'],
            'sectional': ['introduction', 'overview', 'summary', 'conclusion', 'background',
                         'methodology', 'results', 'discussion', 'abstract', 'executive summary'],
            'organizational': ['chapter', 'section', 'part', 'unit', 'module', 'lesson']
        }

    def analyze_font_statistics(self, blocks: List[TextBlock]) -> Dict[str, float]:
        """Analyze font statistics across the document for dynamic thresholding"""
        font_sizes = []
        font_names = []

        for block in blocks:
            if hasattr(block, 'font_size') and block.font_size:
                font_sizes.append(block.font_size)
            if hasattr(block, 'font_name') and block.font_name:
                font_names.append(block.font_name)

        if not font_sizes:
            return {'avg_size': 12.0, 'max_size': 12.0, 'min_size': 12.0, 'std_size': 0.0}

        stats = {
            'avg_size': statistics.mean(font_sizes),
            'max_size': max(font_sizes),
            'min_size': min(font_sizes),
            'std_size': statistics.stdev(font_sizes) if len(font_sizes) > 1 else 0.0,
            'font_variety': len(set(font_names)) if font_names else 1
        }

        # Calculate percentiles for more robust thresholding
        sorted_sizes = sorted(font_sizes)
        n = len(sorted_sizes)
        stats['p75_size'] = sorted_sizes[int(0.75 * n)] if n > 0 else stats['avg_size']
        stats['p90_size'] = sorted_sizes[int(0.90 * n)] if n > 0 else stats['avg_size']

        return stats

    def extract_title_dynamic(self, blocks: List[TextBlock]) -> str:
        """Extract document title using dynamic analysis without hardcoded patterns"""
        if not blocks:
            return ""

        font_stats = self.analyze_font_statistics(blocks)
        title_candidates = []

        # Look at the first 20% of blocks or first 30 blocks, whichever is smaller
        search_limit = min(30, max(10, len(blocks) // 5))

        for i, block in enumerate(blocks[:search_limit]):
            text = block.text.strip()
            if not text or len(text) < 3:
                continue

            # Calculate title likelihood score
            score = 0.0

            # Font size scoring (larger fonts more likely to be titles)
            if hasattr(block, 'font_size') and block.font_size:
                size_ratio = block.font_size / font_stats['avg_size']
                if size_ratio >= 1.5:
                    score += 0.4
                elif size_ratio >= 1.2:
                    score += 0.3
                elif size_ratio >= 1.1:
                    score += 0.2

            # Position scoring (earlier text more likely to be title)
            position_score = max(0, (search_limit - i) / search_limit * 0.3)
            score += position_score

            # Length scoring (reasonable title length)
            word_count = len(text.split())
            if 2 <= word_count <= 15:
                score += 0.2
            elif word_count <= 25:
                score += 0.1

            # Formatting scoring
            if hasattr(block, 'is_bold') and block.is_bold:
                score += 0.1

            # Content pattern scoring
            if re.match(r'^[A-Z]', text):  # Starts with capital
                score += 0.1
            if ':' in text and not text.endswith(':'):  # Contains colon but not ending
                score += 0.1

            # Avoid very short or very long texts
            if len(text) < 10 or len(text) > 200:
                score *= 0.5

            title_candidates.append((text, score, i, block.font_size if hasattr(block, 'font_size') else 0))

        if not title_candidates:
            return blocks[0].text.strip() if blocks else ""

        # Sort by score, then by font size, then by position (earlier is better)
        title_candidates.sort(key=lambda x: (x[1], x[3], -x[2]), reverse=True)

        # Return the best candidate
        return title_candidates[0][0]
    
    def classify_heading_level_dynamic(self, text: str, font_size: float, font_stats: Dict[str, float],
                                      is_bold: bool = False, position_ratio: float = 0.0) -> str:
        """Classify heading level using dynamic analysis without hardcoded patterns"""
        text_clean = text.strip()

        # Calculate relative font size
        avg_font = font_stats['avg_size']
        max_font = font_stats['max_size']
        size_ratio = font_size / avg_font if avg_font > 0 else 1.0

        # Base score for heading level determination
        level_score = 0.0

        # Font size contribution (most important factor)
        if font_size >= max_font * 0.95:  # Very large font
            level_score += 4.0
        elif size_ratio >= 1.4:  # Significantly larger
            level_score += 3.5
        elif size_ratio >= 1.25:  # Moderately larger
            level_score += 3.0
        elif size_ratio >= 1.15:  # Slightly larger
            level_score += 2.5
        elif size_ratio >= 1.05:  # Just above average
            level_score += 2.0
        else:  # Average or below
            level_score += 1.0

        # Formatting contribution
        if is_bold:
            level_score += 0.5

        # Position contribution (earlier content more likely to be higher level)
        level_score += (1.0 - position_ratio) * 0.3

        # Pattern-based adjustments (generic patterns only)
        if re.match(r'^\d+\.\s+', text_clean):  # "1. Introduction"
            level_score += 0.8
        elif re.match(r'^\d+\.\d+\s+', text_clean):  # "1.1 Subsection"
            level_score += 0.4
        elif re.match(r'^\d+\.\d+\.\d+\s+', text_clean):  # "1.1.1 Sub-subsection"
            level_score += 0.2
        elif text_clean.isupper() and len(text_clean.split()) <= 6:  # Short all-caps
            level_score += 0.6
        elif re.match(r'^[A-Z][a-z].*:$', text_clean):  # "Title Case:"
            level_score += 0.3

        # Check for common structural headings
        text_lower = text_clean.lower()
        for category, keywords in self.heading_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if category == 'structural':
                    level_score += 0.7  # Table of contents, references, etc.
                elif category == 'sectional':
                    level_score += 0.5  # Introduction, overview, etc.
                elif category == 'organizational':
                    level_score += 0.4  # Chapter, section, etc.
                break

        # Length penalty for very long text (less likely to be high-level heading)
        word_count = len(text_clean.split())
        if word_count > 15:
            level_score -= 0.5
        elif word_count > 25:
            level_score -= 1.0

        # Determine level based on score
        if level_score >= 3.8:
            return 'H1'
        elif level_score >= 3.0:
            return 'H2'
        elif level_score >= 2.2:
            return 'H3'
        else:
            return 'H4'

    def extract_headings_dynamic(self, blocks: List[TextBlock]) -> List[Dict]:
        """Extract headings using dynamic analysis without document-specific patterns"""
        if not blocks:
            return []

        font_stats = self.analyze_font_statistics(blocks)
        headings = []
        used_texts = set()

        # Analyze document structure to determine if it likely has headings
        total_blocks = len(blocks)

        for i, block in enumerate(blocks):
            text = block.text.strip()
            if not text or len(text) < 2:
                continue

            # Skip duplicates
            if text in used_texts:
                continue

            # Calculate position ratio (0.0 = start, 1.0 = end)
            position_ratio = i / total_blocks if total_blocks > 1 else 0.0

            # Get block properties
            font_size = getattr(block, 'font_size', font_stats['avg_size'])
            is_bold = getattr(block, 'is_bold', False)

            # Calculate heading confidence
            confidence = self._calculate_heading_confidence(
                text, font_size, font_stats, is_bold, position_ratio
            )

            # Apply confidence threshold
            if confidence >= self.confidence_threshold:
                level = self.classify_heading_level_dynamic(
                    text, font_size, font_stats, is_bold, position_ratio
                )

                headings.append({
                    'level': level,
                    'text': text,
                    'page': getattr(block, 'page', 1),
                    'confidence': confidence,
                    'font_size': font_size,
                    'position': i
                })

                used_texts.add(text)

        # Sort by confidence, then by position (earlier is better)
        headings.sort(key=lambda x: (x['confidence'], -x['position']), reverse=True)

        # Dynamic limit based on document length and heading density
        max_headings = self._calculate_dynamic_heading_limit(total_blocks, len(headings))

        # Remove internal fields before returning
        final_headings = []
        for heading in headings[:max_headings]:
            final_headings.append({
                'level': heading['level'],
                'text': heading['text'],
                'page': heading['page']
            })

        return final_headings

    def _calculate_heading_confidence(self, text: str, font_size: float, font_stats: Dict[str, float],
                                    is_bold: bool, position_ratio: float) -> float:
        """Calculate confidence score for heading detection"""
        confidence = 0.0
        text_lower = text.lower()

        # Font size factor (most important)
        size_ratio = font_size / font_stats['avg_size'] if font_stats['avg_size'] > 0 else 1.0
        if size_ratio >= 1.5:
            confidence += 0.4
        elif size_ratio >= 1.25:
            confidence += 0.3
        elif size_ratio >= 1.1:
            confidence += 0.2
        elif size_ratio >= 1.05:
            confidence += 0.1

        # Formatting factors
        if is_bold:
            confidence += 0.15

        # Position factor (earlier content more likely to be headings)
        confidence += (1.0 - position_ratio) * 0.2

        # Pattern-based factors
        for pattern_name, pattern in self.heading_indicators.items():
            if re.match(pattern, text, re.IGNORECASE):
                if pattern_name in ['numbered_section', 'numbered_list']:
                    confidence += 0.25
                elif pattern_name in ['title_case_colon', 'all_caps']:
                    confidence += 0.2
                else:
                    confidence += 0.15
                break

        # Keyword-based factors
        for category, keywords in self.heading_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if category == 'structural':
                    confidence += 0.25
                elif category == 'sectional':
                    confidence += 0.2
                elif category == 'organizational':
                    confidence += 0.15
                break

        # Length factors
        word_count = len(text.split())
        if 2 <= word_count <= 10:
            confidence += 0.1
        elif word_count <= 20:
            confidence += 0.05
        elif word_count > 30:
            confidence -= 0.1

        # Content quality factors
        if text.startswith(text[0].upper()):  # Starts with capital
            confidence += 0.05

        return min(confidence, 1.0)  # Cap at 1.0

    def _calculate_dynamic_heading_limit(self, total_blocks: int, candidate_count: int) -> int:
        """Calculate dynamic limit for number of headings based on document characteristics"""
        # Base limit proportional to document size
        base_limit = max(5, min(50, total_blocks // 20))

        # Adjust based on candidate density
        if candidate_count > base_limit * 2:
            # Too many candidates, be more selective
            return base_limit
        elif candidate_count < base_limit // 2:
            # Few candidates, include more
            return min(candidate_count, base_limit * 2)
        else:
            return base_limit
    
    def process_document(self, blocks: List[TextBlock]) -> Dict[str, Any]:
        """Main processing method using generic document analysis"""
        if not blocks:
            return {'title': '', 'outline': []}

        # Extract title using dynamic analysis
        title = self.extract_title_dynamic(blocks)

        # Extract headings using dynamic analysis
        outline = self.extract_headings_dynamic(blocks)

        return {
            'title': title,
            'outline': outline
        }

def process_pdf_generic(pdf_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """Process PDF with generic heading extraction"""
    logger = setup_logging()

    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count

        # Initialize generic extractor
        extractor = GenericPDFHeadingExtractor(confidence_threshold=confidence_threshold)

        all_blocks = []

        # Extract text blocks from all pages
        for page_num in range(total_pages):
            page = doc[page_num]
            blocks = page.get_text("dict")

            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                # Create text block with enhanced formatting detection
                                font_name = span.get("font", "")
                                text_block = TextBlock(
                                    text=text,
                                    font_name=font_name,
                                    font_size=span.get("size", 12),
                                    font_flags=span.get("flags", 0),
                                    bbox=span.get("bbox", [0, 0, 0, 0]),
                                    page=page_num + 1,
                                    is_bold="Bold" in font_name or "bold" in font_name.lower(),
                                    is_italic="Italic" in font_name or "italic" in font_name.lower()
                                )
                                all_blocks.append(text_block)

        doc.close()

        # Process using generic extractor
        result = extractor.process_document(all_blocks)

        return result

    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        return {
            'title': '',
            'outline': [],
            'error': str(e)
        }

# Backward compatibility function
def process_pdf_hackathon(pdf_path: str) -> Dict[str, Any]:
    """Backward compatibility wrapper for the generic processor"""
    return process_pdf_generic(pdf_path, confidence_threshold=0.5)

def main():
    """Main processing function"""
    print("=" * 80)
    print("HACKATHON GROUND TRUTH OPTIMIZED PDF EXTRACTOR")
    print("=" * 80)
    print("Specifically tuned for provided ground truth examples")
    print("Advanced pattern recognition and document type detection")
    print("Output format: {title: string, outline: [level, text, page]}")
    print("=" * 80)
    
    # Setup
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Find PDFs
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"[ERROR] No PDF files found in {input_dir}")
        return
    
    print(f"[INFO] Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"  - {pdf_file.name} ({size_mb:.1f} MB)")
    
    # Process files
    total_start_time = time.time()
    total_outline_entries = 0
    processing_times = []
    results_summary = []
    
    for pdf_file in pdf_files:
        print(f"\\n[PROCESSING] {pdf_file.name}")
        
        start_time = time.time()
        result = process_pdf_hackathon(str(pdf_file))
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        # Save result in exact ground truth format
        output_file = output_dir / f"{pdf_file.stem}_hackathon_optimized.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"[SAVED] {output_file}")
        
        # Display results
        outline_count = len(result.get('outline', []))
        total_outline_entries += outline_count
        
        print(f"[RESULTS] Title: {result.get('title', 'N/A')}")
        print(f"[RESULTS] Outline entries: {outline_count}")
        
        # Show level distribution
        if outline_count > 0:
            level_counts = Counter(entry['level'] for entry in result['outline'])
            print("[RESULTS] Level distribution:")
            for level, count in sorted(level_counts.items()):
                print(f"  {level}: {count}")
            
            # Show first few entries
            print("[RESULTS] First 5 outline entries:")
            for entry in result['outline'][:5]:
                text_preview = entry['text'][:60] + "..." if len(entry['text']) > 60 else entry['text']
                print(f"  {entry['level']}: {text_preview} (page: {entry['page']})")
        
        print(f"[TIMING] Processing time: {processing_time:.2f}s")
        
        # Store summary
        results_summary.append({
            'file': pdf_file.name,
            'title': result.get('title', ''),
            'outline_entries': outline_count,
            'processing_time': processing_time,
            'has_error': 'error' in result
        })
    
    # Final summary
    total_time = time.time() - total_start_time
    successful_files = len([r for r in results_summary if not r['has_error']])
    failed_files = len(results_summary) - successful_files
    
    print("\\n" + "=" * 80)
    print("HACKATHON PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total files processed: {len(pdf_files)}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")
    print(f"Total outline entries extracted: {total_outline_entries}")
    print(f"Average entries per document: {total_outline_entries / len(pdf_files):.1f}")
    print(f"Total processing time: {total_time:.2f}s")
    print(f"Average time per document: {sum(processing_times) / len(processing_times):.2f}s")
    
    print("\\nOptimized for hackathon ground truth compatibility")
    print("Use ground_truth_analyzer.py to compare with expected results")
    print("=" * 80)

if __name__ == "__main__":
    main()
