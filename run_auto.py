#!/usr/bin/env python3
"""
Автоматическая версия скрипта, которая берет все настройки из config.py
"""

import os
import sys
from datetime import datetime, timedelta
from notion_article_finder import NotionArticleFinder

def load_config():
    """Загрузка конфигурации из файла config.py"""
    try:
        import config
        return (
            config.NOTION_TOKEN, 
            config.DATABASE_ID,
            config.DEFAULT_START_DATE,
            config.DEFAULT_END_DATE,
            config.DEFAULT_OUTPUT_FILE
        )
    except ImportError:
        print("Ошибка: Файл config.py не найден.")
        print("Создайте файл config.py на основе config_example.py")
        return None, None, None, None, None
    except AttributeError as e:
        print(f"Ошибка в config.py: {e}")
        print("Убедитесь, что все необходимые переменные определены в config.py")
        return None, None, None, None, None

def get_date_range():
    """Получение диапазона дат от пользователя или использование значений по умолчанию"""
    print("=== Настройка диапазона дат ===")
    print("1. Использовать даты из config.py")
    print("2. Ввести свои даты")
    print("3. Последние 30 дней")
    
    choice = input("Выберите вариант (1-3): ").strip()
    
    if choice == "1":
        return None, None  # Используем значения по умолчанию
    elif choice == "2":
        while True:
            start_date = input("Начальная дата (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Неверный формат даты. Используйте YYYY-MM-DD")
        
        while True:
            end_date = input("Конечная дата (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Неверный формат даты. Используйте YYYY-MM-DD")
        
        return start_date, end_date
    elif choice == "3":
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return start_date, end_date
    else:
        print("Неверный выбор. Используем значения по умолчанию.")
        return None, None

def main():
    """Главная функция"""
    print("=== Notion Article Finder (Автоматический режим) ===")
    
    # Загрузка конфигурации
    notion_token, database_id, default_start, default_end, default_output = load_config()
    if not all([notion_token, database_id, default_start, default_end, default_output]):
        return
    
    print(f"Токен: {notion_token[:10]}...")
    print(f"База данных: {database_id}")
    print(f"Даты по умолчанию: {default_start} - {default_end}")
    print()
    
    # Получение диапазона дат
    start_date, end_date = get_date_range()
    
    # Используем значения по умолчанию, если не выбраны свои
    if not start_date:
        start_date = default_start
    if not end_date:
        end_date = default_end
    
    # Получение имени выходного файла
    output_file = input(f"Имя выходного файла (Enter для {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    print(f"\nПоиск статей с {start_date} по {end_date}...")
    print(f"Результат будет сохранен в: {output_file}")
    print()
    
    # Создание и запуск поисковика
    try:
        finder = NotionArticleFinder(notion_token, database_id)
        finder.run(start_date, end_date, output_file)
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")
        print("Проверьте правильность токена и ID базы данных в config.py")

if __name__ == "__main__":
    main()
