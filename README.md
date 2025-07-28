# Challenge 1A: PDF Outline Extraction

## Overview
This solution extracts structured outlines from PDF documents, identifying titles and hierarchical headings (H1, H2, H3) with their page locations using advanced font-based analysis. It forms the foundation for Challenge 1B's intelligent document analysis. 

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

## Usage

### Docker Execution

```bash
# Build
docker build -t phase1a .

# Run  
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" phase1a
```
