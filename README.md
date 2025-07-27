# Advanced Offline PDF Heading Extractor

A comprehensive, modular PDF heading extraction system that works 100% offline using only PyMuPDF and standard Python libraries. This system uses multi-signal analysis to accurately detect titles, H1, H2, and H3 headings from any type of PDF document.

## Features

### 🎯 **Multi-Signal Heading Detection**
- **Font Analysis**: Size, style, weight, and family analysis
- **Content Analysis**: Linguistic patterns and keyword recognition
- **Pattern Recognition**: Numbering schemes and structural patterns
- **Spatial Analysis**: Position, spacing, and layout analysis
- **Context Analysis**: Surrounding text and document flow

### 📄 **Supported Document Types**
- ✅ Research papers and academic documents
- ✅ Technical reports and specifications  
- ✅ Business documents and presentations
- ✅ Resumes and CVs
- ✅ Books and manuals
- ✅ Forms and structured documents

### 📊 **Multiple Output Formats**
- **JSON**: Detailed metadata and structured data
- **CSV**: Spreadsheet-friendly tabular format
- **TXT**: Human-readable outline format

### ⚙️ **Advanced Configuration**
- Configurable confidence thresholds
- Hierarchical validation and correction
- Font analysis parameters
- Export format selection

## Project Structure

```
Adobe_Round-1A/
├── input/                          # Place PDF files here
├── output/                         # Generated results
├── main_offline.py                 # Main processing script
├── extractor.py                    # PDF text extraction module
├── classifier.py                   # Heading classification module
├── font_analyzer.py                # Font hierarchy analysis
├── pattern_recognizer.py           # Pattern and structure recognition
├── text_processor.py               # Text analysis and processing
├── data_structures.py              # Core data structures
├── utils.py                        # Utility functions
├── demo_and_config.py              # Configuration and demo script
├── debug_analysis.py               # Debug and analysis tool
└── README.md                       # This file
```

## Installation and Requirements

### Prerequisites
- Python 3.7+
- PyMuPDF (fitz) - `pip install PyMuPDF`

### Installation
```bash
# Clone or download the project
cd Adobe_Round-1A

# Install PyMuPDF (only external dependency)
pip install PyMuPDF

# The system is ready to use!
```

## Quick Start

### 1. Basic Usage
```bash
# Place PDF files in the 'input/' directory
mkdir input
# Copy your PDF files to input/

# Run the extraction system
python main_offline.py
```

### 2. Check Results
Results are saved in the `output/` directory in three formats:
- `filename_headings_offline.json` - Detailed structured data
- `filename_headings_offline_headings.csv` - Tabular format
- `filename_headings_offline_outline.txt` - Human-readable outline

## Advanced Usage

### Debug Analysis
```bash
# Analyze classification scores and font hierarchy
python debug_analysis.py
```

### Configuration Demo
```bash
# See advanced features and configuration options
python demo_and_config.py
```

### Custom Processing
```python
from extractor import OfflinePDFHeadingExtractor

# Initialize with custom confidence threshold
extractor = OfflinePDFHeadingExtractor()
results = extractor.process_pdf_offline("document.pdf", confidence_threshold=0.3)

# Process results
headings = results['headings']
for heading in headings:
    print(f"{heading['level']}: {heading['text']} (confidence: {heading['confidence']:.2f})")
```

## Module Documentation

### Core Modules

#### `main_offline.py`
Main processing script with comprehensive error handling, performance monitoring, and multi-format output generation.

#### `extractor.py` 
PDF text extraction and block analysis. Handles PyMuPDF integration and text block enhancement.

#### `classifier.py`
Multi-signal heading classification system combining font, content, pattern, spatial, and context analysis.

#### `font_analyzer.py`
Font hierarchy analysis including size distribution, style analysis, and heading likelihood scoring.

#### `pattern_recognizer.py`
Pattern recognition for numbering schemes, capitalization patterns, and structural elements.

#### `text_processor.py`
Text analysis including tokenization, stopword removal, and linguistic feature extraction.

#### `data_structures.py`
Core data structures including the `TextBlock` class with comprehensive metadata.

#### `utils.py`
Utility functions for hierarchy validation, multi-format export, and result post-processing.

## Configuration Options

### ExtractorConfig Class
```python
class ExtractorConfig:
    confidence_threshold = 0.25           # Minimum heading confidence
    title_confidence_threshold = 0.3     # Minimum title confidence
    min_font_size_ratio = 1.1            # Font size ratio threshold
    max_heading_words = 15               # Maximum words in heading
    include_low_confidence = False       # Include low-confidence headings
    export_formats = ['json', 'csv', 'txt']  # Output formats
    validate_hierarchy = True            # Enable hierarchy validation
```

## Performance

### Typical Performance Metrics
- **Processing Speed**: 0.02-0.20 seconds per document
- **Memory Usage**: Low memory footprint
- **Accuracy**: High precision with configurable recall

### Performance Example
```
Total files processed: 6
Successful: 6
Failed: 0
Total headings extracted: 34
Average headings per document: 5.7
Total processing time: 0.55s
Average time per document: 0.09s
```

## Output Examples

### JSON Output
```json
{
  "title": "Research Paper Title",
  "headings": [
    {
      "level": "h1",
      "text": "Introduction",
      "page": 1,
      "font_size": 14.5,
      "confidence": 0.89,
      "bbox": [72, 150, 200, 165],
      "features": {
        "word_count": 1,
        "is_bold": true,
        "caps_ratio": 0.09,
        "numbering": {"type": null, "number": null, "title": "Introduction"}
      }
    }
  ],
  "metadata": {
    "total_blocks": 156,
    "confidence_threshold": 0.25,
    "processing_method": "offline_comprehensive"
  }
}
```

### CSV Output
```csv
Level,Text,Page,Font Size,Confidence,Word Count
h1,Introduction,1,14.5,0.89,1
h2,Background,1,12.0,0.75,1
h2,Methodology,2,12.0,0.82,1
```

### TXT Outline
```
TITLE: Research Paper Title
==================================================

  H1: Introduction (Page 1)
    H2: Background (Page 1)
    H2: Methodology (Page 2)
  H1: Results (Page 3)
    H2: Analysis (Page 3)
```

## Architecture

### Multi-Signal Classification Pipeline

1. **Text Extraction**: PyMuPDF extracts text blocks with font metadata
2. **Feature Analysis**: Multiple feature extractors analyze each block
3. **Font Hierarchy**: Statistical analysis of font usage patterns
4. **Classification**: Weighted combination of multiple signals
5. **Validation**: Hierarchical structure validation and correction
6. **Export**: Multi-format output generation

### Signal Weights
- Font Size & Style: 40% (25% + 15%)
- Content Analysis: 20%
- Pattern Matching: 15%
- Context Analysis: 15%
- Spatial Features: 10%

## Troubleshooting

### Common Issues

#### No Headings Detected
- Lower the confidence threshold: `confidence_threshold=0.15`
- Check debug output: `python debug_analysis.py`
- Verify PDF has extractable text (not scanned image)

#### Too Many False Positives
- Increase confidence threshold: `confidence_threshold=0.35`
- Reduce maximum heading words: `max_heading_words=10`

#### Incorrect Hierarchy
- Enable hierarchy validation: `validate_hierarchy=True`
- Check font hierarchy in debug output

### Debug Commands
```bash
# Analyze specific document
python debug_analysis.py

# Test different confidence thresholds
python demo_and_config.py

# Verbose processing
python main_offline.py  # Check console output
```

## Integration Notes

### Seamless Module Integration
This refactored codebase integrates advanced modular components while preserving your existing logic:

1. **Preserved Functionality**: All original PDF processing capabilities maintained
2. **Enhanced Analysis**: Added multi-signal classification and font hierarchy analysis
3. **Improved Structure**: Clean separation of concerns across modules
4. **Backward Compatibility**: Existing interfaces preserved where possible
5. **Extended Features**: Added configuration, debugging, and multiple output formats

### Migration from Previous Version
- ✅ All existing PDF processing logic preserved
- ✅ Enhanced with advanced classification algorithms
- ✅ Improved error handling and validation
- ✅ Added comprehensive configuration options
- ✅ Maintained offline-only operation

## License

This project uses only standard Python libraries and PyMuPDF for maximum compatibility and offline operation.

## Contributing

To extend the system:
1. Add new signal analysis in `classifier.py`
2. Extend pattern recognition in `pattern_recognizer.py`
3. Add new output formats in `utils.py`
4. Enhance font analysis in `font_analyzer.py`

## Support

For issues or questions:
1. Check the debug output: `python debug_analysis.py`
2. Review configuration options: `python demo_and_config.py`
3. Examine the JSON output for detailed analysis results

