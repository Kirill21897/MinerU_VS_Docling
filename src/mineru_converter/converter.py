import os
import sys
import json
import time
import shutil
from pathlib import Path
from glob import glob

# Add the MinerU source code to the python path
# Assuming this script is running from src/mineru_converter or similar depth
# We need to find the root of the project to locate src/MinerU
# Adjust logic: if we are in src/mineru_converter, project root is ../../
# MinerU src is at ../MinerU

def setup_mineru_path():
    current_file_path = Path(__file__).resolve()
    # Go up to 'src'
    src_dir = current_file_path.parent.parent
    mineru_src_path = src_dir / "MinerU"
    
    if str(mineru_src_path) not in sys.path:
        sys.path.insert(0, str(mineru_src_path))

setup_mineru_path()

try:
    from mineru.backend.pipeline.pipeline_analyze import doc_analyze
    from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json
    from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make
    from mineru.data.data_reader_writer import FileBasedDataWriter
    from mineru.utils.enum_class import MakeMode
except ImportError as e:
    print(f"Error importing MinerU modules: {e}")
    print("Please ensure the 'src/MinerU' directory exists and dependencies are installed.")
    # We don't exit here to allow other parts of the app to run if needed, but this module won't work
    
class MinerUConverter:
    def __init__(self, input_dir, output_dir, device="cpu"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.device = device
        
        # Ensure output directory exists
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
    def convert(self, file_name, lang="ch"):
        """
        Convert a single PDF file to Markdown.
        """
        file_path = self.input_dir / file_name
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        print(f"[MinerU] Processing: {file_name}...")
        
        # Read PDF content
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            
        # Run analysis (Pipeline Backend)
        try:
            # pdf_bytes_list, lang_list, parse_method, formula_enable, table_enable
            infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = doc_analyze(
                pdf_bytes_list=[pdf_bytes],
                lang_list=[lang],
                parse_method='auto',
                formula_enable=True,
                table_enable=True
            )
        except Exception as e:
            print(f"[MinerU] Error during analysis of {file_name}: {e}")
            return

        # Process results
        for idx, model_list in enumerate(infer_results):
            # Prepare local output paths
            file_stem = file_path.stem
            # We want to keep MinerU outputs separate or identifiable
            # Let's put them in output_dir directly, maybe with a suffix or subfolder if managed by caller
            # Here we follow the passed output_dir
            
            local_image_dir = self.output_dir / "images"
            local_md_dir = self.output_dir 
            
            # Ensure image directory exists
            if not local_image_dir.exists():
                local_image_dir.mkdir(parents=True, exist_ok=True)

            image_writer = FileBasedDataWriter(str(local_image_dir))
            md_writer = FileBasedDataWriter(str(local_md_dir))

            images_list = all_image_lists[idx]
            pdf_doc = all_pdf_docs[idx]
            _lang = lang_list[idx]
            _ocr_enable = ocr_enabled_list[idx]
            
            # Convert model output to middle json
            middle_json = result_to_middle_json(
                model_list, images_list, pdf_doc, image_writer,
                _lang, _ocr_enable, formula_enabled=True
            )
            
            pdf_info = middle_json["pdf_info"]
            
            # Generate Markdown
            image_dir_name = "images" # Relative path for markdown images
            md_content = union_make(pdf_info, MakeMode.MM_MD, image_dir_name)
            
            # Save Markdown
            md_file_path = local_md_dir / f"{file_stem}_mineru.md"
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            print(f"[MinerU] Successfully converted: {file_name} -> {md_file_path}")

    def run_batch(self):
        """
        Process all PDF files in the input directory.
        """
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"[MinerU] No PDF files found in {self.input_dir}")
            return

        print(f"[MinerU] Found {len(pdf_files)} PDF files in {self.input_dir}")
        
        for pdf_file in pdf_files:
            self.convert(pdf_file.name)
