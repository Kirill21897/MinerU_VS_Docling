import argparse
import sys
from pathlib import Path
import os
import time

try:
    from docling.document_converter import DocumentConverter
except ImportError as e:
    print(f"Error importing Docling: {e}")
    
class DoclingConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert(self, file_name):
        file_path = self.input_dir / file_name
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        print(f"[Docling] Processing: {file_name}...")
        
        start_time = time.time()
        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)
            
            markdown_content = result.document.export_to_markdown()
            
            output_filename = f"{file_path.stem}_docling.md"
            output_path = self.output_dir / output_filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            elapsed = time.time() - start_time
            print(f"[Docling] Successfully converted: {file_name} -> {output_path}")
            print(f"[Docling] Time taken: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"[Docling] Error processing {file_name}: {e}")

    def run_batch(self):
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"[Docling] No PDF files found in {self.input_dir}")
            return

        print(f"[Docling] Found {len(pdf_files)} PDF files in {self.input_dir}")
        
        for pdf_file in pdf_files:
            self.convert(pdf_file.name)
