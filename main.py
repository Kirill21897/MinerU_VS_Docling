import argparse
import os
import sys
from pathlib import Path

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Configuration for MinerU (Must be set before importing MinerU modules)
config_file = os.path.join(current_dir, "mineru.json")
models_dir = os.path.join(current_dir, "models")

if os.path.exists(config_file):
    os.environ['MINERU_TOOLS_CONFIG_JSON'] = config_file
    if os.path.exists(models_dir) and os.listdir(models_dir):
        os.environ['MINERU_MODEL_SOURCE'] = 'local'
    else:
        print(f"Warning: Models directory empty or not found at {models_dir}")
        print("Please run 'python scripts/download_models.py' to setup models.")

# Import converters
try:
    from mineru_converter.converter import MinerUConverter
except ImportError:
    MinerUConverter = None
    print("Warning: MinerU converter not available. Check src/mineru_converter.")

try:
    from docling_converter.converter import DoclingConverter
except ImportError:
    DoclingConverter = None
    print("Warning: Docling converter not available. Check src/docling_converter.")

def main():
    parser = argparse.ArgumentParser(description="PDF to Markdown Converter Comparison Tool")
    parser.add_argument("--mode", choices=["mineru", "docling", "all"], default="all", help="Converter to run")
    parser.add_argument("--input", default=os.path.join("data", "raw"), help="Input directory")
    parser.add_argument("--output", default=os.path.join("data", "processed"), help="Output directory")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    print(f"--- Starting Conversion Task ---")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Mode: {args.mode}")
    print("-" * 30)

    # Run MinerU
    if args.mode in ["mineru", "all"]:
        if MinerUConverter:
            print("\n>>> Running MinerU Converter...")
            mineru = MinerUConverter(input_dir, output_dir)
            mineru.run_batch()
        else:
            print("\n>>> Skipping MinerU (Not installed/configured)")

    # Run Docling
    if args.mode in ["docling", "all"]:
        if DoclingConverter:
            print("\n>>> Running Docling Converter...")
            docling = DoclingConverter(input_dir, output_dir)
            docling.run_batch()
        else:
            print("\n>>> Skipping Docling (Not installed/configured)")

    print("\n--- Task Completed ---")

if __name__ == "__main__":
    main()
