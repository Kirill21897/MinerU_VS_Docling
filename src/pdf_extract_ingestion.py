import sys
import os
import logging
from pathlib import Path
from time import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add PDF-Extract-Kit source to sys.path
PDF_EXTRACT_KIT_ROOT = PROJECT_ROOT / "src" / "PDF-Extract-Kit-main"
sys.path.insert(0, str(PDF_EXTRACT_KIT_ROOT))

from config.config import RAW_DIR, PROCESSED_DIR

# Import PDF-Extract-Kit modules
try:
    from pdf_extract_kit.utils.config_loader import initialize_tasks_and_models
    from pdf_extract_kit.tasks.pdf2markdown import PDF2MARKDOWN
except ImportError as e:
    logger.error(f"Import Error: {e}. Check PYTHONPATH.")
    sys.exit(1)

def run_pdf_extract_ingestion(source_file: str = 'Sample.pdf'):
    # Ensure processed directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    source_path = RAW_DIR / source_file
    if not source_path.exists():
        logger.error(f"File not found: {source_path}")
        return

    logger.info(f"Starting processing: {source_path} with PDF-Extract-Kit...")
    
    # Models root directory
    MODELS_ROOT = PROJECT_ROOT / "models" / "models"
    
    # Configuration dictionary with absolute paths
    config = {
        'inputs': str(source_path),
        'outputs': str(PROCESSED_DIR),
        'visualize': False,
        'merge2markdown': True,
        'tasks': {
            'layout_detection': {
                'model': 'layout_detection_yolo',
                'model_config': {
                    'img_size': 1024,
                    'conf_thres': 0.25,
                    'iou_thres': 0.45,
                    'model_path': str(MODELS_ROOT / "Layout/YOLO/doclayout_yolo_ft.pt")
                }
            },
            'formula_detection': {
                'model': 'formula_detection_yolo',
                'model_config': {
                    'img_size': 1280,
                    'conf_thres': 0.25,
                    'iou_thres': 0.45,
                    'batch_size': 1,
                    'model_path': str(MODELS_ROOT / "MFD/YOLO/yolo_v8_ft.pt")
                }
            },
            'formula_recognition': {
                'model': 'formula_recognition_unimernet',
                'model_config': {
                    'batch_size': 128,
                    'cfg_path': str(PDF_EXTRACT_KIT_ROOT / "pdf_extract_kit/configs/unimernet.yaml"),
                    'model_path': str(MODELS_ROOT / "MFR/unimernet_tiny")
                }
            },
            'ocr': {
                'model': 'ocr_ppocr',
                'model_config': {
                    'lang': 'ch', 
                    'show_log': True,
                    'det_model_dir': str(MODELS_ROOT / "OCR/PaddleOCR/det/ch_PP-OCRv4_det"),
                    'rec_model_dir': str(MODELS_ROOT / "OCR/PaddleOCR/rec/ch_PP-OCRv4_rec"),
                    'det_db_box_thresh': 0.3
                }
            }
        }
    }
    
    start_time = time()
    try:
        # Initialize models
        task_instances = initialize_tasks_and_models(config)
        
        layout_model = task_instances['layout_detection'].model if 'layout_detection' in task_instances else None
        mfd_model = task_instances['formula_detection'].model if 'formula_detection' in task_instances else None
        mfr_model = task_instances['formula_recognition'].model if 'formula_recognition' in task_instances else None
        ocr_model = task_instances['ocr'].model if 'ocr' in task_instances else None
        
        # Initialize PDF2MARKDOWN task
        pdf_extract_task = PDF2MARKDOWN(layout_model, mfd_model, mfr_model, ocr_model)
        
        # Run processing
        extract_results = pdf_extract_task.process(
            str(source_path), 
            save_dir=str(PROCESSED_DIR), 
            visualize=False, 
            merge2markdown=True
        )
        
        elapsed = time() - start_time
        
        # Rename output file to match naming convention if needed
        # pdf_extract_kit saves as {basename}.md
        # We might want to rename it to {basename}_pdf_extract.md to avoid conflict?
        # But for now, let's keep it as is or log the location.
        basename = source_path.stem
        output_md = PROCESSED_DIR / f"{basename}.md"
        
        logger.info(f"Document successfully processed. Results at: {PROCESSED_DIR}")
        if output_md.exists():
             logger.info(f"Markdown file: {output_md}")
             
        logger.info(f"Execution time: {elapsed:.2f} s")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run PDF-Extract-Kit ingestion")
    parser.add_argument("--file", type=str, default="Sample.pdf", help="Filename in data/raw")
    args = parser.parse_args()
    
    run_pdf_extract_ingestion(args.file)
