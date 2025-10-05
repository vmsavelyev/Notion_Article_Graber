"""
Пример конфигурационного файла для Notion Article Finder
Скопируйте этот файл в config.py и заполните своими данными
"""

# Токен доступа к Notion API
# Получите его в https://www.notion.so/my-integrations
NOTION_TOKEN = ""

# ID базы данных "Обзор рынка технологии машинного обучения"
# Находится в URL базы данных между / и ?
DATABASE_ID = ""

# Настройки по умолчанию
DEFAULT_START_DATE = "2025-10-01"
DEFAULT_END_DATE = "2025-10-03"
DEFAULT_OUTPUT_FILE = "notion_articles_urls.txt"
