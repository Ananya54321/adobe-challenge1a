import os
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
import pdfplumber
import time
from typing import List, Dict, Any


class PDFOutlineExtractor:
    def __init__(self):
        """Initialize the PDF outline extractor with font-based analysis"""
        pass
    
    def extract_font_lines(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text with font information using pdfplumber"""
        font_lines = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    lines_by_y = defaultdict(list)
                    
                    for char in page.chars:
                        y = round(char["top"], 1)   
                        lines_by_y[y].append(char)
                    
                    for y in sorted(lines_by_y):
                        chars = lines_by_y[y]
                        sorted_chars = sorted(chars, key=lambda x: x["x0"])
                        text = "".join(c["text"] for c in sorted_chars)
                        
                        font_size = round(sum(float(c["size"]) for c in chars) / len(chars), 2)
                        
                        if text.strip(): 
                            font_lines.append({
                                "text": text.strip(),
                                "font_size": font_size,
                                "page": page_num,
                                "y": y
                            })
        
        except Exception as e:
            print(f"Error extracting font information from {pdf_path}: {e}")
            return []
        
        return font_lines
    
    def classify_headings(self, lines: List[Dict[str, Any]]) -> tuple:
        """Classify headings based on font sizes and content patterns"""
        if not lines:
            return "Untitled Document", []
        
        heading_candidates = [l for l in lines if len(l['text']) < 100]
        
        if not heading_candidates:
            return "Untitled Document", []
        
        font_size_counts = Counter([l["font_size"] for l in heading_candidates])
        
        sorted_fonts = sorted(font_size_counts.items(), key=lambda x: (-x[0], -x[1]))
        
        top_fonts = [fs for fs, _ in sorted_fonts[:5]]
        
        font_to_level = {}
        levels = ["Title", "H1", "H2", "H3", "H4"]
        for i, fs in enumerate(top_fonts):
            font_to_level[fs] = levels[i]
        
        title = None
        outline = []
        
        for line in heading_candidates:
            level = font_to_level.get(line["font_size"])
            if not level:
                continue
            
            text = line["text"].strip()
            
            if level == "Title" and not title:
                title = text
            else:
                if level in ["H1", "H2", "H3"]:
                    if self.is_valid_heading_simple(text):
                        outline.append({
                            "level": level,
                            "text": text,
                            "page": line["page"]
                        })
        
        return title or "Untitled Document", outline
    
    def is_valid_heading_simple(self, text: str) -> bool:
        """Simple validation for headings"""
        if not any(c.isalpha() for c in text):
            return False
        
        if len(text) < 3:
            return False
        
        if re.match(r'^\d+$', text):  
            return False
        
        if re.search(r'^\d+\.\d+.*\d{4}', text):  
            return False
        
        return True
    
    def clean_heading_text(self, text: str) -> str:
        """Clean and normalize heading text"""
        text = re.sub(r'\s+', ' ', text.strip())
        
        text = re.sub(r'^[^\w]*', '', text)   
        text = re.sub(r'[^\w\s\.\d]*$', '', text) 
        
        return text.strip()
    
    def is_toc_artifact(self, text: str) -> bool:
        """Filter out table of contents artifacts and page numbers"""
        if re.match(r'^[\d\s\.]+$', text):
            return True
        
        if re.match(r'^[\.]+\s*\d+$', text):
            return True
        
        return False
    
    def extract_title_from_structure(self, lines: List[Dict[str, Any]]) -> str:
        """Extract title by analyzing document structure"""
        if not lines:
            return "Untitled Document"
        
        first_page_lines = [l for l in lines if l['page'] == 1]
        
        if not first_page_lines:
            return "Untitled Document"
        
        max_font_size = max(l['font_size'] for l in first_page_lines)
        large_font_lines = [l for l in first_page_lines if l['font_size'] >= max_font_size - 2]
        
        for line in large_font_lines:
            text = self.clean_heading_text(line['text'])
            if (5 < len(text) < 100 and 
                not self.is_likely_body_text(text) and
                self.is_valid_heading(text)):
                return text
        
        for line in first_page_lines[:5]:
            text = self.clean_heading_text(line['text'])
            if 5 < len(text) < 100:
                return text
        
        return "Untitled Document"
    
    def is_likely_body_text(self, text: str) -> bool:
        """Check if text is likely body text rather than a heading"""
        if text.endswith('.') and len(text) > 30:
            return True
        
        if text.count('.') > 1:
            return True
        
        if sum(1 for c in text if c.islower()) > len(text) * 0.6:
            return True
        
        if re.search(r'version\s+\d+', text, re.IGNORECASE):
            return True
        
        if re.search(r'\d{4}.*page\s+\d+', text, re.IGNORECASE):
            return True
        
        if re.search(r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', text, re.IGNORECASE):
            return True
        
        if re.search(r'\d+\.\d+.*\d{4}', text):
            return True
        
        if re.match(r'^[\d\s\.\-\:]+$', text):
            return True
        
        skip_patterns = [
            r'^\d+$',  # Just numbers
            r'^page\s+\d+',  # Page numbers
            r'©.*copyright',  # Copyright notices
            r'www\.',  # URLs
            r'@',  # Email addresses
            r'^\d+\.\d+\s+\d+\s+\w+\s+\d{4}',  # Version dates
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def is_valid_heading(self, text: str) -> bool:
        """Validate if text is a proper heading"""
        if not any(c.isalpha() for c in text):
            return False
        
        if len(text) < 3:
            return False
        
        if re.match(r'^[\d\s\W]+$', text):
            return False
        
        if re.search(r'^\d+\.\d+.*\d{4}', text):
            return False
        
        if re.search(r'^\d+\.\d+.*\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', text, re.IGNORECASE):
            return False
        
        if re.search(r'(initial version|reviewed and confirmed|amended)', text, re.IGNORECASE):
            return False
        
        if sum(1 for c in text if c.isalpha()) < 3:
            return False
        
        return True
    
    def extract_title_fallback(self, lines: List[Dict[str, Any]]) -> str:
        """Extract title from first page when font-based approach fails"""
        if not lines:
            return "Untitled Document"
        
        first_page_lines = [l for l in lines if l['page'] == 1][:10]
        
        for line in first_page_lines:
            text = self.clean_heading_text(line['text'])
            if (len(text) > 5 and len(text) < 100 and 
                not self.is_likely_body_text(text) and
                any(c.isalpha() for c in text)):
                return text
        
        return "Untitled Document"
    
    def process_pdf(self, pdf_path: str, output_path: str):
        """Process a single PDF and generate outline JSON"""
        start_time = time.time()
        
        print(f"Processing {os.path.basename(pdf_path)}...")
        
        font_lines = self.extract_font_lines(pdf_path)
        
        if not font_lines:
            print(f"No content extracted from {pdf_path}")
            output_data = {
                "title": "Untitled Document",
                "outline": []
            }
        else:
            title, outline = self.classify_headings(font_lines)
            
            output_data = {
                "title": title,
                "outline": outline
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        processing_time = time.time() - start_time
        print(f"Processed {os.path.basename(pdf_path)} in {processing_time:.2f}s -> {os.path.basename(output_path)}")
        print(f"Found title: '{output_data['title']}' and {len(output_data['outline'])} headings")


def main():
    """Main execution function"""
    print("Starting PDF outline extraction...")
    
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    if not input_dir.exists():
        input_dir = Path("./input")
        output_dir = Path("./output")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        extractor.process_pdf(str(pdf_file), str(output_file))
    
    print("Processing completed!")


if __name__ == "__main__":
    main()