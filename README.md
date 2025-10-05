# Notion Article Finder

Скрипт для поиска статей в Notion Database "Обзор рынка технологии машинного обучения" по дате и экспорта их в CSV формат с названиями, URL статей и Notion URL.

## Установка

1. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

**Примечание**: Скрипт работает на Python 3. Используйте `python3` и `pip3` команды.

2. Получите токен доступа к Notion API:
   - Перейдите в [Notion Developers](https://www.notion.so/my-integrations)
   - Создайте новую интеграцию
   - Скопируйте "Internal Integration Token"

3. Получите ID базы данных:
   - Откройте базу данных в Notion
   - Скопируйте ID из URL (32-символьная строка между `/` и `?`)

## Использование

### Автоматический режим (рекомендуется)

```bash
python3 run_auto.py
```

Этот скрипт автоматически загружает настройки из `config.py` и предоставляет интерактивный интерфейс для выбора дат.

### Ручной режим

```bash
python3 notion_article_finder.py \
  --token YOUR_NOTION_TOKEN \
  --database-id YOUR_DATABASE_ID \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### С настройкой выходного файла

```bash
python3 notion_article_finder.py \
  --token YOUR_NOTION_TOKEN \
  --database-id YOUR_DATABASE_ID \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --output my_articles.csv
```

## Настройка

### Создание конфигурационного файла

1. Скопируйте `config_example.py` в `config.py`:
```bash
cp config_example.py config.py
```

2. Отредактируйте `config.py` и заполните ваши данные:
```python
NOTION_TOKEN = "ваш_токен_здесь"
DATABASE_ID = "ваш_id_базы_данных_здесь"
DEFAULT_START_DATE = "2025-10-01"
DEFAULT_END_DATE = "2025-10-03"
DEFAULT_OUTPUT_FILE = "notion_articles.csv"
```

## Параметры

- `--token` - Токен доступа к Notion API (обязательный)
- `--database-id` - ID базы данных Notion (обязательный)
- `--start-date` - Начальная дата поиска в формате YYYY-MM-DD (обязательный)
- `--end-date` - Конечная дата поиска в формате YYYY-MM-DD (обязательный)
- `--output` - Путь к выходному файлу (по умолчанию: notion_articles.csv)

## Примеры

### Автоматический режим

```bash
# Запуск с интерактивным интерфейсом
python3 run_auto.py

# Выберите вариант:
# 1. Использовать даты из config.py
# 2. Ввести свои даты
# 3. Последние 30 дней
```

### Ручной режим

```bash
# Поиск статей за последний месяц
python3 notion_article_finder.py \
  --token not_1234567890abcdef \
  --database-id 12345678-90ab-cdef-1234-567890abcdef \
  --start-date 2024-01-01 \
  --end-date 2024-01-31

# Поиск статей за конкретную неделю
python3 notion_article_finder.py \
  --token not_1234567890abcdef \
  --database-id 12345678-90ab-cdef-1234-567890abcdef \
  --start-date 2024-01-15 \
  --end-date 2024-01-21 \
  --output weekly_articles.csv
```

## Выходной файл

Скрипт создает CSV файл со следующими колонками:

| Колонка | Описание |
|---------|----------|
| **Название статьи** | Название статьи из поля "Name" |
| **URL статьи** | Ссылка на оригинальную статью из поля "URL" |
| **Notion URL** | Ссылка на страницу в Notion |

### Пример CSV файла:

```csv
Название статьи,URL статьи,Notion URL
"OpenAI acquires AI startup for personalization","https://techcrunch.com/2025/10/03/...","https://notion.so/283140d42a858123b2d6cb7f3b53d05c"
"Machine Learning Trends 2025","https://example.com/ml-trends","https://notion.so/abcdef1234567890abcdef1234567890"
...
```

## Тестирование

### Единый тест и диагностика

Запустите полный тест всех функций:

```bash
python3 test_unified.py
```

Этот тест включает:
- ✅ **Диагностику структуры БД** - проверяет поля и их типы
- ✅ **Тест подключения к API** - проверяет токен и доступ
- ✅ **Поиск статей** - тестирует разные диапазоны дат
- ✅ **Извлечение данных** - названия и URL статей
- ✅ **Экспорт в CSV** - сохранение результатов
- ✅ **Проверку качества** - анализ извлеченных данных
- ✅ **Подробную статистику** - процент успешности

### Быстрая диагностика

Если нужна только диагностика структуры базы данных:

```bash
python3 debug_notion.py
```

## Структура проекта

```
├── notion_article_finder.py    # Основной скрипт
├── run_auto.py                 # Автоматический режим (рекомендуется)
├── test_unified.py             # Единый тест и диагностика
├── debug_notion.py             # Быстрая диагностика БД
├── config.py                   # Конфигурация (создать из config_example.py)
├── config_example.py           # Пример конфигурации
├── requirements.txt            # Зависимости Python
└── README.md                   # Документация
```

## Важные замечания

1. **Доступ к базе данных**: Убедитесь, что ваша интеграция Notion имеет доступ к базе данных
2. **Поля в базе данных**:
   - Поле "Date" типа Date (для фильтрации по дате)
   - Поле "Name" типа Title (для названий статей)
   - Поле "URL" типа URL (для ссылок на статьи)
3. **Формат даты**: YYYY-MM-DD
4. **Пагинация**: Скрипт автоматически обрабатывает пагинацию результатов Notion API
5. **CSV формат**: Результаты сохраняются в CSV с правильным экранированием кавычек и запятых
