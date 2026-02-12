import argparse
import sys
from pathlib import Path

# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from docling_ingestion import run_docling_ingestion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск конвертации через Docling")
    parser.add_argument("--file", type=str, default="Sample.pdf", help="Имя файла в data/raw")
    args = parser.parse_args()
    
    run_docling_ingestion(args.file)
