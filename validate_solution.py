#!/usr/bin/env python3
"""
Validation script for Challenge 1A
Tests the PDF outline extraction solution
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys

def validate_output_format(output_file):
    """Validate the JSON output format"""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required fields
        if 'title' not in data:
            return False, "Missing 'title' field"
        
        if 'outline' not in data:
            return False, "Missing 'outline' field"
        
        if not isinstance(data['outline'], list):
            return False, "'outline' must be a list"
        
        # Check outline items
        for i, item in enumerate(data['outline']):
            if not isinstance(item, dict):
                return False, f"outline[{i}] must be an object"
            
            required_fields = ['level', 'text', 'page']
            for field in required_fields:
                if field not in item:
                    return False, f"outline[{i}] missing '{field}' field"
            
            # Validate level values
            if item['level'] not in ['H1', 'H2', 'H3']:
                return False, f"outline[{i}] has invalid level: {item['level']}"
            
            # Validate page number
            if not isinstance(item['page'], int) or item['page'] < 1:
                return False, f"outline[{i}] has invalid page number: {item['page']}"
        
        return True, "Valid format"
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"

def test_challenge_1a():
    """Test Challenge 1A solution"""
    print("Testing Challenge 1A Solution...")
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Copy sample PDFs if available
        sample_pdfs = Path("sample_dataset/pdfs")
        if sample_pdfs.exists():
            for pdf_file in sample_pdfs.glob("*.pdf"):
                shutil.copy2(pdf_file, input_dir)
        else:
            print("Warning: No sample PDFs found. Please add PDFs to test.")
            return False
        
        # Build Docker image
        print("Building Docker image...")
        build_result = subprocess.run([
            "docker", "build", "--platform", "linux/amd64", 
            "-t", "challenge1a:test", "."
        ], capture_output=True, text=True)
        
        if build_result.returncode != 0:
            print(f"Docker build failed: {build_result.stderr}")
            return False
        
        # Run Docker container
        print("Running Docker container...")
        run_result = subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{input_dir}:/app/input:ro",
            "-v", f"{output_dir}:/app/output",
            "--network", "none",
            "challenge1a:test"
        ], capture_output=True, text=True, timeout=60)
        
        if run_result.returncode != 0:
            print(f"Docker run failed: {run_result.stderr}")
            return False
        
        # Validate outputs
        print("Validating outputs...")
        pdf_files = list(input_dir.glob("*.pdf"))
        success = True
        
        for pdf_file in pdf_files:
            expected_output = output_dir / f"{pdf_file.stem}.json"
            if not expected_output.exists():
                print(f"Missing output file: {expected_output.name}")
                success = False
                continue
            
            is_valid, message = validate_output_format(expected_output)
            if is_valid:
                print(f"✓ {expected_output.name}: {message}")
            else:
                print(f"✗ {expected_output.name}: {message}")
                success = False
        
        return success

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    success = test_challenge_1a()
    sys.exit(0 if success else 1)
