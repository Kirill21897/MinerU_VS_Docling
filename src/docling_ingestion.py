import sys
import argparse
import logging
from pathlib import Path
from time import time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Добавить корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from docling.document_converter import DocumentConverter
    from config.config import RAW_DIR, PROCESSED_DIR
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}. Убедитесь, что установлены все зависимости и корректен PYTHONPATH.")
    sys.exit(1)

def run_docling_ingestion(source_file: str = 'Sample.pdf'):
    # Убедимся, что целевая директория существует
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    source_path = RAW_DIR / source_file
    if not source_path.exists():
        logger.error(f"Файл не найден: {source_path}")
        return

    logger.info(f"Начинаем обработку файла: {source_path} с помощью Docling...")
    
    start_time = time()
    try:
        converter = DocumentConverter()
        result = converter.convert(source_path)
        
        markdown_content = result.document.export_to_markdown()
        
        output_filename = f"{source_path.stem}_docling.md"
        output_path = PROCESSED_DIR / output_filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        elapsed = time() - start_time
        logger.info(f"Документ успешно сохранён в файл: {output_path.resolve()}")
        logger.info(f"Время выполнения: {elapsed:.2f} сек.")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск Docling ingestion")
    parser.add_argument("--file", type=str, default="Sample.pdf", help="Имя файла в data/raw")
    args = parser.parse_args()
    
    run_docling_ingestion(args.file)