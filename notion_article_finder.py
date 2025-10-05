#!/usr/bin/env python3
"""
Скрипт для поиска статей в Notion Database по дате и сохранения их URL-ов в файл.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse
import json


class NotionArticleFinder:
    def __init__(self, notion_token: str, database_id: str):
        """
        Инициализация клиента Notion API
        
        Args:
            notion_token: Токен доступа к Notion API
            database_id: ID базы данных "Обзор рынка технологии машинного обучения"
        """
        self.notion_token = notion_token
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def search_articles_by_date(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Поиск статей в базе данных по дате
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            
        Returns:
            Список найденных статей
        """
        url = f"{self.base_url}/databases/{self.database_id}/query"
        
        # Формируем фильтр по дате
        filter_data = {
            "filter": {
                "and": [
                    {
                        "property": "Date",
                        "date": {
                            "on_or_after": start_date
                        }
                    },
                    {
                        "property": "Date", 
                        "date": {
                            "on_or_before": end_date
                        }
                    }
                ]
            }
        }
        
        all_results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            if start_cursor:
                filter_data["start_cursor"] = start_cursor
            
            try:
                response = requests.post(url, headers=self.headers, json=filter_data)
                response.raise_for_status()
                
                data = response.json()
                all_results.extend(data.get("results", []))
                
                has_more = data.get("has_more", False)
                start_cursor = data.get("next_cursor")
                
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к Notion API: {e}")
                return []
        
        return all_results
    
    def extract_articles_info(self, articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Извлечение информации о статьях (название, URL статьи и Notion URL)
        
        Args:
            articles: Список статей из Notion
            
        Returns:
            Список словарей с информацией о статьях
        """
        articles_info = []
        
        for article in articles:
            # Получаем Notion URL страницы
            page_id = article["id"]
            notion_url = f"https://notion.so/{page_id.replace('-', '')}"
            
            # Получаем название статьи
            title = "Без названия"
            properties = article.get('properties', {})
            
            # Ищем поле с названием статьи (обычно это title или Name)
            for field_name in ['Name', 'Title', 'Название', 'Заголовок', 'title', 'name']:
                if field_name in properties:
                    field_value = properties[field_name]
                    if field_value.get('type') == 'title' and field_value.get('title'):
                        title = field_value['title'][0].get('text', {}).get('content', 'Без названия')
                        break
                    elif field_value.get('type') == 'rich_text' and field_value.get('rich_text'):
                        title = field_value['rich_text'][0].get('text', {}).get('content', 'Без названия')
                        break
                    elif field_value.get('type') == 'text' and field_value.get('text'):
                        title = field_value['text'][0].get('content', 'Без названия')
                        break
            
            # Получаем URL статьи из поля URL
            article_url = "Нет URL"
            for field_name in ['URL', 'url', 'Url', 'Ссылка', 'ссылка']:
                if field_name in properties:
                    field_value = properties[field_name]
                    if field_value.get('type') == 'url' and field_value.get('url'):
                        article_url = field_value['url']
                        break
                    elif field_value.get('type') == 'rich_text' and field_value.get('rich_text'):
                        rich_text = field_value['rich_text']
                        if rich_text and rich_text[0].get('text', {}).get('link', {}).get('url'):
                            article_url = rich_text[0]['text']['link']['url']
                            break
                        elif rich_text and rich_text[0].get('text', {}).get('content'):
                            article_url = rich_text[0]['text']['content']
                            break
            
            articles_info.append({
                'title': title,
                'article_url': article_url,
                'notion_url': notion_url
            })
        
        return articles_info
    
    def save_articles_to_file(self, articles_info: List[Dict[str, str]], output_file: str):
        """
        Сохранение информации о статьях в CSV файл
        
        Args:
            articles_info: Список информации о статьях (название, URL статьи, Notion URL)
            output_file: Путь к выходному файлу
        """
        try:
            # Определяем расширение файла
            if not output_file.endswith('.csv'):
                output_file = output_file.replace('.txt', '.csv')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Записываем заголовки CSV
                f.write("Название статьи,URL статьи,Notion URL\n")
                
                # Записываем данные
                for article in articles_info:
                    # Экранируем кавычки и запятые в названии
                    title = article['title'].replace('"', '""')
                    if ',' in title or '"' in title:
                        title = f'"{title}"'
                    
                    # Экранируем URL
                    article_url = article['article_url'].replace('"', '""')
                    if ',' in article_url or '"' in article_url:
                        article_url = f'"{article_url}"'
                    
                    notion_url = article['notion_url'].replace('"', '""')
                    if ',' in notion_url or '"' in notion_url:
                        notion_url = f'"{notion_url}"'
                    
                    f.write(f"{title},{article_url},{notion_url}\n")
            
            print(f"Статьи успешно сохранены в CSV файл: {output_file}")
            print(f"Найдено статей: {len(articles_info)}")
            
        except IOError as e:
            print(f"Ошибка при сохранении файла: {e}")
    
    def run(self, start_date: str, end_date: str, output_file: str = "notion_articles_urls.txt"):
        """
        Основной метод для выполнения поиска и сохранения информации о статьях
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD
            output_file: Путь к выходному файлу
        """
        print(f"Поиск статей с {start_date} по {end_date}...")
        
        # Поиск статей
        articles = self.search_articles_by_date(start_date, end_date)
        
        if not articles:
            print("Статьи не найдены или произошла ошибка при поиске.")
            return
        
        # Извлечение информации о статьях (название и URL)
        articles_info = self.extract_articles_info(articles)
        
        # Сохранение в файл
        self.save_articles_to_file(articles_info, output_file)


def main():
    """Главная функция с настройкой аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Поиск статей в Notion Database по дате")
    parser.add_argument("--token", required=True, help="Notion API токен")
    parser.add_argument("--database-id", required=True, help="ID базы данных Notion")
    parser.add_argument("--start-date", required=True, help="Начальная дата (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="Конечная дата (YYYY-MM-DD)")
    parser.add_argument("--output", default="notion_articles_urls.txt", help="Выходной файл")
    
    args = parser.parse_args()
    
    # Валидация дат
    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
        datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        print("Ошибка: Неверный формат даты. Используйте YYYY-MM-DD")
        return
    
    # Создание и запуск поисковика
    finder = NotionArticleFinder(args.token, args.database_id)
    finder.run(args.start_date, args.end_date, args.output)


if __name__ == "__main__":
    main()
