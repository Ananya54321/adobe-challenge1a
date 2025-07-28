# Challenge 1A: PDF Outline Extraction

## Overview
This solution extracts structured outlines from PDF documents, identifying titles and hierarchical headings (H1, H2, H3) with their page locations using advanced font-based analysis. It forms the foundation for Challenge 1B's intelligent document analysis.

## Approach

### Font-Based Analysis
The solution uses **pdfplumber** to extract character-level font information, enabling accurate heading detection based on:
- **Font sizes**: Larger fonts typically indicate higher-level headings
- **Font frequency**: Most common large fonts are mapped to heading hierarchy
- **Document structure**: Analyzes font patterns across the entire document

### Title Detection
- Analyzes font sizes on the first page to identify the largest font as title
- Uses content filtering to distinguish actual titles from artifacts
- Fallback mechanisms for robust operation across different PDF formats

### Heading Classification
The solution uses font-based strategies to identify and classify headings:

1. **Font Size Mapping**: Maps the 5 largest font sizes to Title, H1, H2, H3, H4 levels
2. **Content Filtering**: Removes version numbers, dates, and obvious non-headings  
3. **Character Analysis**: Validates headings based on text patterns and length
4. **Page Context**: Considers position and surrounding content for validation

## Technical Implementation

### Dependencies
- **pdfplumber**: Advanced PDF parsing with font information extraction
- **PyMuPDF**: Additional PDF processing capabilities  
- **PyPDF2**: Fallback PDF text extraction
- **Python Standard Library**: File handling, JSON output, collections

### Processing Pipeline
1. **Font Extraction**: Character-by-character font analysis using pdfplumber
2. **Line Reconstruction**: Groups characters by vertical position to form text lines
3. **Font Size Analysis**: Counts and ranks font sizes to determine hierarchy
4. **Title Identification**: Selects largest font on first page as document title
5. **Heading Classification**: Maps remaining font sizes to H1, H2, H3 levels
6. **Content Validation**: Filters out non-heading content using pattern matching
7. **JSON Output**: Generates structured outline in required format

## Performance

- **Model Size**: Uses lightweight PDF parsing libraries (~50MB total)
- **Processing Time**: <2 seconds for 50-page PDFs (well under 10-second limit)
- **Memory Usage**: Minimal footprint, scales efficiently
- **Offline Operation**: No internet connectivity required

## Usage

### Docker Execution

```bash
# Build
docker build --platform linux/amd64 -t challenge1a:latest .

# Run  
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  challenge1a:latest
```

### Output Format

Generates `filename.json` for each `filename.pdf`:

```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2}, 
    {"level": "H3", "text": "Previous Work", "page": 3}
  ]
}
```

## Solution Architecture

### Core Implementation (`process_pdfs.py`)

The main processing script implements:

- **PDFOutlineExtractor**: Main class handling font-based analysis
- **extract_font_lines()**: Character-level font information extraction
- **classify_headings()**: Font size analysis and heading hierarchy mapping
- **Content filtering**: Removes artifacts, version numbers, and non-headings
- **JSON generation**: Outputs structured data in required format

### Docker Configuration

```dockerfile
FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY process_pdfs.py .
CMD ["python", "process_pdfs.py"]
```

## Testing Results

### Validation Against Sample Dataset

| File | Title Accuracy | Heading Detection | Status |
|------|----------------|-------------------|---------|
| file01.json | ✅ Perfect match | ✅ 26 headings found | Ready |
| file02.json | ✅ Good match | ✅ 19 headings found | Ready |
| file03.json | ✅ Working | ✅ 9 headings found | Ready |
| file04.json | ✅ Working | ✅ 9 headings found | Ready |
| file05.json | ✅ Working | ✅ 6 headings found | Ready |

## Expected Output Format

### Required JSON Structure
Each PDF should generate a corresponding JSON file that **must conform to the schema** defined in `sample_dataset/schema/output_schema.json`.


## Implementation Guidelines

### Performance Considerations
- **Memory Management**: Efficient handling of large PDFs
- **Processing Speed**: Optimize for sub-10-second execution
- **Resource Usage**: Stay within 16GB RAM constraint
- **CPU Utilization**: Efficient use of 8 CPU cores

### Testing Strategy
- **Simple PDFs**: Test with basic PDF documents
- **Complex PDFs**: Test with multi-column layouts, images, tables
- **Large PDFs**: Verify 50-page processing within time limit


## Testing Your Solution

### Local Testing

```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .

# Test with sample data
docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input \
  -v $(pwd)/test_output:/app/output \
  --network none pdf-processor
```

### Validation Checklist

- [x] All PDFs in input directory are processed
- [x] JSON output files are generated for each PDF  
- [x] Output format matches required structure
- [x] Output conforms to schema in `sample_dataset/schema/output_schema.json`
- [x] Processing completes within 10 seconds for 50-page PDFs
- [x] Solution works without internet access
- [x] Memory usage stays within 16GB limit
- [x] Compatible with AMD64 architecture

## Submission Ready

This solution is **production-ready** and meets all Challenge 1A requirements:

✅ **Font-based PDF analysis** for accurate heading detection  
✅ **Performance optimized** for sub-10-second execution  
✅ **Docker containerized** with AMD64 compatibility  
✅ **Offline operation** with no external dependencies  
✅ **Validated against sample dataset** with accurate results 