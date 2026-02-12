# config\config.py
"""
config.py - Конфигурация приложения
Использует переменные окружения для безопасного хранения секретов.
"""

from pathlib import Path

# Базовые директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"