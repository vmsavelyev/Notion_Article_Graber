#!/usr/bin/env python3
"""
Единый тест и диагностика Notion Article Finder
Объединяет диагностику структуры БД и полное тестирование функционала
"""

from notion_article_finder import NotionArticleFinder
from config import NOTION_TOKEN, DATABASE_ID
import requests
import os

def diagnose_database_structure():
    """Диагностика структуры базы данных"""
    
    print("🔍 ДИАГНОСТИКА СТРУКТУРЫ БАЗЫ ДАННЫХ")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Получаем информацию о базе данных
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        db_title = data.get('title', [{}])[0].get('text', {}).get('content', 'Неизвестно')
        print(f"✅ База данных: {db_title}")
        print(f"✅ ID: {data.get('id')}")
        print()
        
        # Показываем поля
        properties = data.get('properties', {})
        print("📋 Поля в базе данных:")
        
        required_fields = {'Date': False, 'Name': False, 'URL': False}
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"   - {prop_name}: {prop_type}")
            
            # Проверяем нужные поля
            if prop_name == 'Date' and prop_type == 'date':
                required_fields['Date'] = True
                print(f"     ✅ Поле даты найдено")
            elif prop_name == 'Name' and prop_type == 'title':
                required_fields['Name'] = True
                print(f"     ✅ Поле названий найдено")
            elif prop_name == 'URL' and prop_type == 'url':
                required_fields['URL'] = True
                print(f"     ✅ Поле URL найдено")
        
        print()
        
        # Проверяем наличие всех нужных полей
        missing_fields = [field for field, found in required_fields.items() if not found]
        if missing_fields:
            print(f"⚠️  Отсутствуют поля: {', '.join(missing_fields)}")
            print("   Это может повлиять на работу скрипта")
        else:
            print("✅ Все необходимые поля найдены!")
        
        return True, required_fields
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при подключении к базе данных: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Статус код: {e.response.status_code}")
            print(f"   Ответ: {e.response.text}")
        return False, {}

def test_api_connection():
    """Тестирование подключения к API"""
    
    print("\n🔌 ТЕСТ ПОДКЛЮЧЕНИЯ К API")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Простой запрос
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        query_data = {"page_size": 1}
        
        response = requests.post(url, headers=headers, json=query_data)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ API подключение работает")
            print(f"✅ Найдено записей: {len(results)}")
            
            if results:
                print("✅ Есть данные для тестирования")
                return True, results[0]
            else:
                print("⚠️  База данных пуста")
                return True, None
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False, None

def test_article_search():
    """Тестирование поиска статей"""
    
    print("\n📊 ТЕСТ ПОИСКА СТАТЕЙ")
    print("-" * 50)
    
    finder = NotionArticleFinder(NOTION_TOKEN, DATABASE_ID)
    
    # Тестовые диапазоны дат
    test_ranges = [
        {
            "name": "Широкий диапазон (2024-2025)",
            "start": "2024-01-01",
            "end": "2025-12-31"
        },
        {
            "name": "Октябрь 2025",
            "start": "2025-10-01",
            "end": "2025-10-31"
        },
        {
            "name": "1-3 октября 2025",
            "start": "2025-10-01",
            "end": "2025-10-03"
        }
    ]
    
    successful_tests = []
    
    for i, test_range in enumerate(test_ranges, 1):
        print(f"\n{i}. {test_range['name']}")
        print(f"   Период: {test_range['start']} - {test_range['end']}")
        
        try:
            articles = finder.search_articles_by_date(test_range['start'], test_range['end'])
            
            if articles:
                print(f"   ✅ Найдено статей: {len(articles)}")
                
                # Показываем первые 2 статьи
                for j, article in enumerate(articles[:2], 1):
                    page_id = article["id"]
                    page_url = f"https://notion.so/{page_id.replace('-', '')}"
                    print(f"      {j}. {page_url}")
                    
                    # Показываем дату
                    date_prop = article.get('properties', {}).get('Date', {})
                    date_value = date_prop.get('date', 'Нет даты')
                    print(f"         Дата: {date_value}")
                
                if len(articles) > 2:
                    print(f"      ... и еще {len(articles) - 2} статей")
                
                test_range['articles'] = articles
                test_range['status'] = 'success'
                successful_tests.append(test_range)
                
            else:
                print(f"   ⚠️  Статьи не найдены")
                test_range['status'] = 'no_articles'
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            test_range['status'] = 'error'
            test_range['error'] = str(e)
    
    return successful_tests

def test_data_extraction(articles):
    """Тестирование извлечения данных"""
    
    print("\n📝 ТЕСТ ИЗВЛЕЧЕНИЯ ДАННЫХ")
    print("-" * 50)
    
    finder = NotionArticleFinder(NOTION_TOKEN, DATABASE_ID)
    
    try:
        # Извлекаем информацию о статьях
        articles_info = finder.extract_articles_info(articles)
        
        print(f"✅ Извлечение данных успешно!")
        print(f"✅ Обработано статей: {len(articles_info)}")
        
        # Статистика
        titles_found = sum(1 for a in articles_info if a['title'] != 'Без названия')
        urls_found = sum(1 for a in articles_info if a['article_url'] != 'Нет URL')
        
        print(f"\n📈 Статистика извлечения:")
        print(f"   - Названия: {titles_found}/{len(articles_info)} ({titles_found/len(articles_info)*100:.1f}%)")
        print(f"   - URL статей: {urls_found}/{len(articles_info)} ({urls_found/len(articles_info)*100:.1f}%)")
        
        # Показываем первые 3 статьи
        print(f"\n📋 Примеры извлеченных данных:")
        for i, article in enumerate(articles_info[:3], 1):
            print(f"\n{i}. Название: {article['title']}")
            print(f"   URL статьи: {article['article_url']}")
            print(f"   Notion URL: {article['notion_url']}")
        
        if len(articles_info) > 3:
            print(f"\n... и еще {len(articles_info) - 3} статей")
        
        return articles_info, titles_found, urls_found
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении данных: {e}")
        import traceback
        traceback.print_exc()
        return [], 0, 0

def test_csv_export(articles_info):
    """Тестирование экспорта в CSV"""
    
    print("\n💾 ТЕСТ ЭКСПОРТА В CSV")
    print("-" * 50)
    
    if not articles_info:
        print("❌ Нет данных для экспорта")
        return False
    
    try:
        finder = NotionArticleFinder(NOTION_TOKEN, DATABASE_ID)
        
        # Сохраняем в CSV
        csv_file = "unified_test_results.csv"
        finder.save_articles_to_file(articles_info, csv_file)
        
        print(f"✅ CSV файл создан: {csv_file}")
        
        # Проверяем файл
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            print(f"✅ Размер файла: {file_size} байт")
            
            # Показываем первые строки
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"✅ Строк в файле: {len(lines)}")
                print(f"✅ Заголовки: {lines[0].strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        return False

def check_data_quality(articles_info):
    """Проверка качества данных"""
    
    print("\n🔍 ПРОВЕРКА КАЧЕСТВА ДАННЫХ")
    print("-" * 50)
    
    if not articles_info:
        print("❌ Нет данных для проверки")
        return
    
    quality_issues = []
    
    # Проверяем названия
    empty_titles = [a for a in articles_info if a['title'] == 'Без названия']
    if empty_titles:
        quality_issues.append(f"Статей без названий: {len(empty_titles)}")
    
    # Проверяем URL статей
    empty_urls = [a for a in articles_info if a['article_url'] == 'Нет URL']
    if empty_urls:
        quality_issues.append(f"Статей без URL: {len(empty_urls)}")
    
    # Проверяем длину названий
    short_titles = [a for a in articles_info if len(a['title']) < 10]
    if short_titles:
        quality_issues.append(f"Коротких названий (<10 символов): {len(short_titles)}")
    
    if quality_issues:
        print("⚠️  Обнаружены проблемы качества:")
        for issue in quality_issues:
            print(f"   - {issue}")
    else:
        print("✅ Качество данных отличное!")

def main():
    """Главная функция единого теста"""
    
    print("=" * 60)
    print("🔍 ЕДИНЫЙ ТЕСТ И ДИАГНОСТИКА NOTION ARTICLE FINDER")
    print("=" * 60)
    print(f"Токен: {NOTION_TOKEN[:10]}...")
    print(f"Database ID: {DATABASE_ID}")
    print()
    
    # Шаг 1: Диагностика структуры БД
    db_ok, required_fields = diagnose_database_structure()
    if not db_ok:
        print("❌ Не удалось подключиться к базе данных. Проверьте токен и ID.")
        return
    
    # Шаг 2: Тест подключения к API
    api_ok, sample_record = test_api_connection()
    if not api_ok:
        print("❌ Не удалось подключиться к API. Проверьте токен.")
        return
    
    # Шаг 3: Тест поиска статей
    successful_tests = test_article_search()
    if not successful_tests:
        print("❌ Не удалось найти статьи. Проверьте диапазон дат.")
        return
    
    # Берем первый успешный тест
    test_case = successful_tests[0]
    articles = test_case['articles']
    
    # Шаг 4: Тест извлечения данных
    articles_info, titles_found, urls_found = test_data_extraction(articles)
    if not articles_info:
        print("❌ Не удалось извлечь данные из статей.")
        return
    
    # Шаг 5: Тест экспорта в CSV
    export_ok = test_csv_export(articles_info)
    
    # Шаг 6: Проверка качества данных
    check_data_quality(articles_info)
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    print(f"✅ Диагностика БД: {'Успешно' if db_ok else 'Ошибка'}")
    print(f"✅ Подключение API: {'Успешно' if api_ok else 'Ошибка'}")
    print(f"✅ Поиск статей: {len(successful_tests)} успешных тестов")
    print(f"✅ Извлечение данных: {len(articles_info)} статей")
    print(f"✅ Экспорт CSV: {'Успешно' if export_ok else 'Ошибка'}")
    
    if articles_info:
        print(f"\n📊 Статистика:")
        print(f"   - Названия: {titles_found}/{len(articles_info)} ({titles_found/len(articles_info)*100:.1f}%)")
        print(f"   - URL статей: {urls_found}/{len(articles_info)} ({urls_found/len(articles_info)*100:.1f}%)")
        print(f"   - Результат сохранен в: unified_test_results.csv")
    
    print("\n🎉 Единый тест завершен!")

if __name__ == "__main__":
    main()
