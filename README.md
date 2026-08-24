# Data Analysis API Service

## Описание
API-сервис для загрузки, анализа и очистки данных (CSV/Excel) с использованием Flask, Pandas и PostgreSQL.

## Технологии
- Python 3.10
- Flask
- Pandas
- SQLAlchemy + PostgreSQL
- Matplotlib / Seaborn (для графиков)

## Установка и запуск
1. Клонируйте репозиторий.
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте: `venv\Scripts\activate` (Windows)
4. Установите зависимости: `pip install -r requirements.txt`
5. Создайте базу данных PostgreSQL `data_analyzer`.
6. Настройте `.env` (укажите DATABASE_URL).
7. Выполните миграции: `flask db upgrade`
8. Запустите сервер: `python run.py`

## Примеры запросов
- Загрузка файла:  
  `curl -X POST -F "file=@test.csv" http://127.0.0.1:5000/api/upload`
- Получение статистики:  
  `curl "http://127.0.0.1:5000/api/data/stats?file_id=1"`
- Очистка данных:  
  `curl "http://127.0.0.1:5000/api/data/clean?file_id=1&method=mean&format=json"`
- Построение графика:  
  `curl "http://127.0.0.1:5000/api/data/plot?file_id=1&x=age&y=salary&type=scatter"`
