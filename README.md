# Generic PDF Heading Extractor

A robust, document-agnostic PDF heading extraction system that works across different PDF formats and layouts. This project was developed for the Adobe Hackathon Round 1A to extract structured headings and titles from PDF documents.

## Our Approach

### Core Philosophy
Our solution employs a **generic, document-agnostic approach** that doesn't rely on hardcoded patterns or document-specific rules. Instead, it uses dynamic analysis to understand document structure and extract headings based on:

1. **Font Analysis**: Dynamic font size statistics to identify relative importance
2. **Position Analysis**: Early content positioning for title and heading detection
3. **Pattern Recognition**: Generic patterns like numbered sections, bullet points, and formatting cues
4. **Content Analysis**: Keyword-based detection for structural elements
5. **Confidence Scoring**: Multi-factor scoring system to rank heading candidates

### Key Features

#### Dynamic Title Extraction
- Analyzes the first 20% of document blocks or first 30 blocks
- Uses font size ratios, position scoring, and content patterns
- Considers formatting (bold, capitalization) and reasonable title length

#### Adaptive Heading Detection
- Calculates document-wide font statistics for dynamic thresholding
- Uses confidence scoring based on multiple factors:
  - Font size relative to document average
  - Text formatting (bold, italic)
  - Position within document
  - Pattern matching (numbered sections, bullet points)
  - Keyword recognition (introduction, summary, etc.)
  - Content quality metrics

#### Hierarchical Classification
- Automatically classifies headings into levels (H1, H2, H3, H4)
- Based on font size ratios, formatting, and structural patterns
- No hardcoded document-specific rules

#### Robust Processing
- Handles various PDF formats and layouts
- Error handling and fallback mechanisms
- Configurable confidence thresholds

## Models and Libraries Used

### Core Dependencies
- **PyMuPDF (fitz) v1.23.4**: Primary PDF processing library
  - Text extraction with detailed formatting information
  - Font metadata extraction (size, name, flags)
  - Bounding box information for spatial analysis

### Built-in Python Libraries
- **json**: Output formatting and serialization
- **logging**: Error handling and debugging
- **re**: Regular expression pattern matching
- **statistics**: Font size analysis and statistical calculations
- **time**: Performance monitoring
- **pathlib**: File system operations
- **typing**: Type hints for better code maintainability
- **collections.Counter**: Level distribution analysis
- **dataclasses**: Structured data representation

### Custom Components
- **TextBlock**: Custom data structure for comprehensive text metadata
- **GenericPDFHeadingExtractor**: Main extraction engine with dynamic analysis
- **Font Statistics Analyzer**: Dynamic document analysis for adaptive thresholding

## How to Build and Run Your Solution

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

#### Option 1: Local Installation
```bash
# Clone or download the project
cd Adobe_Round-1A

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Docker Installation
```bash
# Build the Docker image
docker build -t pdf-heading-extractor .

# Run with Docker
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-heading-extractor
```

### Usage

#### Basic Usage
```bash
# Process all PDFs in the input directory
python main_hackathon_optimized.py
```

#### Input Setup
1. Place your PDF files in the `input/` directory
2. The system will automatically detect and process all `.pdf` files

#### Output
- Results are saved in the `output/` directory
- Each PDF generates a corresponding JSON file with the format: `{filename}_hackathon_optimized.json`
- Output format:
```json
{
    "title": "Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Heading Text",
            "page": 1
        }
    ]
}
```

### Configuration Options

#### Confidence Threshold
You can adjust the heading detection sensitivity by modifying the confidence threshold in the code:

```python
# In main_hackathon_optimized.py
extractor = GenericPDFHeadingExtractor(confidence_threshold=0.5)  # Default: 0.5
```

- Lower values (0.3-0.4): More headings detected, potentially more false positives
- Higher values (0.6-0.8): Fewer headings detected, higher precision

### Project Structure
```
Adobe_Round-1A/
├── main_hackathon_optimized.py    # Main processing script
├── data_structures.py             # TextBlock data structure
├── ground_truth_analyzer.py       # Analysis utilities
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
├── input/                         # Input PDF files
├── output/                        # Generated JSON results
└── README.md                      # This file
```

### Performance Characteristics
- **Processing Speed**: ~2-5 seconds per document (varies by size and complexity)
- **Memory Usage**: Optimized for large documents with streaming processing
- **Accuracy**: Tuned for high precision with configurable recall
- **Scalability**: Batch processing support for multiple documents

### Troubleshooting

#### Common Issues
1. **No PDFs found**: Ensure PDF files are in the `input/` directory
2. **Permission errors**: Check file permissions for input/output directories
3. **Memory issues**: For very large PDFs, consider processing individually

#### Debug Mode
Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Testing and Validation
Use the included ground truth analyzer to compare results:
```bash
python ground_truth_analyzer.py
```

This tool helps validate extraction accuracy against expected results and provides detailed analysis of the extraction performance.

### Algorithm Details

#### Font Statistics Analysis
The system calculates comprehensive font statistics including:
- Average, minimum, maximum font sizes
- Standard deviation for size variation
- 75th and 90th percentile thresholds
- Font variety metrics

#### Confidence Scoring Algorithm
Each potential heading is scored based on:
- **Font Size Factor (40% weight)**: Relative size compared to document average
- **Position Factor (20% weight)**: Earlier content scores higher
- **Pattern Factor (25% weight)**: Numbered sections, bullet points, formatting
- **Keyword Factor (15% weight)**: Structural and sectional keywords

#### Dynamic Thresholding
- Adapts to document characteristics
- Prevents over-extraction in dense documents
- Ensures minimum quality standards

### Technical Implementation

#### Text Extraction Pipeline
1. **PDF Parsing**: PyMuPDF extracts text with formatting metadata
2. **Block Creation**: Convert spans to TextBlock objects with enhanced properties
3. **Statistical Analysis**: Calculate document-wide font and formatting statistics
4. **Title Detection**: Analyze early content for document title
5. **Heading Classification**: Score and classify potential headings
6. **Level Assignment**: Hierarchical classification based on multiple factors
7. **Output Generation**: Format results in standardized JSON structure

#### Error Handling
- Graceful degradation for corrupted PDFs
- Fallback mechanisms for missing metadata
- Comprehensive logging for debugging
- Input validation and sanitization
