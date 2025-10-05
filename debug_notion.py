#!/usr/bin/env python3
"""
Диагностический скрипт для проверки структуры базы данных Notion
"""

import requests
import json
from config import NOTION_TOKEN, DATABASE_ID

def check_database_structure():
    """Проверяет структуру базы данных и выводит все поля"""
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Получаем информацию о базе данных
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    
    try:
        print("=== Проверка базы данных ===")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"Название базы данных: {data.get('title', [{}])[0].get('text', {}).get('content', 'Неизвестно')}")
        print(f"ID базы данных: {data.get('id')}")
        print()
        
        print("=== Поля в базе данных ===")
        properties = data.get('properties', {})
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"- {prop_name}: {prop_type}")
            
            # Если это поле даты, показываем дополнительную информацию
            if prop_type == 'date':
                print(f"  └─ Поле даты найдено: '{prop_name}'")
        
        print()
        
        # Пробуем получить несколько записей без фильтра
        print("=== Тестовый запрос (первые 5 записей) ===")
        query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        query_data = {"page_size": 5}
        
        response = requests.post(query_url, headers=headers, json=query_data)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        print(f"Найдено записей: {len(results)}")
        
        if results:
            print("\nПример записи:")
            first_result = results[0]
            print(f"ID: {first_result.get('id')}")
            print("Поля:")
            
            for prop_name, prop_value in first_result.get('properties', {}).items():
                prop_type = prop_value.get('type', 'unknown')
                print(f"  - {prop_name} ({prop_type}): {prop_value}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Notion API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Статус код: {e.response.status_code}")
            print(f"Ответ: {e.response.text}")
        return False

def test_date_field():
    """Тестирует разные варианты названий полей даты"""
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Возможные названия полей даты
    possible_date_fields = [
        "Дата", "Date", "дата", "date", 
        "Дата создания", "Created", "created",
        "Дата публикации", "Published", "published",
        "Время", "Time", "время", "time"
    ]
    
    print("\n=== Тестирование полей даты ===")
    
    for field_name in possible_date_fields:
        print(f"Тестируем поле: '{field_name}'")
        
        query_data = {
            "filter": {
                "property": field_name,
                "date": {
                    "is_not_empty": True
                }
            },
            "page_size": 1
        }
        
        try:
            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            response = requests.post(url, headers=headers, json=query_data)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                print(f"  ✅ Поле '{field_name}' работает! Найдено записей: {len(results)}")
                return field_name
            else:
                print(f"  ❌ Поле '{field_name}' не работает (код: {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ Ошибка с полем '{field_name}': {e}")
    
    return None

if __name__ == "__main__":
    print("=== Диагностика Notion Database ===")
    print(f"Токен: {NOTION_TOKEN[:10]}...")
    print(f"Database ID: {DATABASE_ID}")
    print()
    
    # Проверяем структуру базы данных
    if check_database_structure():
        # Тестируем поля даты
        working_date_field = test_date_field()
        
        if working_date_field:
            print(f"\n✅ Найдено рабочее поле даты: '{working_date_field}'")
            print("Обновите скрипт, заменив 'Дата' на это поле.")
        else:
            print("\n❌ Не найдено рабочее поле даты.")
            print("Проверьте, есть ли в базе данных поле с датами.")
