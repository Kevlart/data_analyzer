
# Data Analysis API Service

REST API для загрузки, анализа и очистки данных из CSV и Excel файлов.

## Возможности

- Загрузка файлов форматов CSV, XLSX, XLS
- Вычисление среднего, медианы и корреляции для числовых колонок
- Очистка данных: удаление дубликатов, заполнение пропусков (mean, median, drop)
- Построение графиков (scatter, histogram) в формате base64
- Хранение данных и результатов в PostgreSQL

## Технологии

- Python 3.10+
- Flask
- Pandas, NumPy
- Matplotlib, Seaborn
- PostgreSQL, SQLAlchemy
- Flask-Migrate

## Установка и запуск

1. Клонируйте репозиторий:
   
   git clone https://github.com/ваш-логин/data_analyzer.git
   cd data_analyzer
   

2. Создайте виртуальное окружение:
   
   python -m venv venv
   
   Активация:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Установите зависимости:
   
   pip install -r requirements.txt
   

4. Настройте PostgreSQL:
   - Убедитесь, что сервер PostgreSQL запущен.
   - Создайте базу данных:
     
     CREATE DATABASE data_analyzer;
     

5. Настройте переменные окружения:
   Скопируйте `.env.example` в `.env` и укажите свои данные:
   
   SECRET_KEY=ваш-секретный-ключ
   DATABASE_URL=postgresql://пользователь:пароль@localhost:5432/data_analyzer
   

6. Примените миграции:
   
   flask db upgrade
   
   Если команда не найдена, используйте `python -m flask db upgrade`.

7. Запустите сервер:
   
   python run.py
   
   Сервер будет доступен по адресу: `http://127.0.0.1:5000`

## Примеры запросов (через curl)

### Загрузка файла

curl -X POST -F "file=@test.csv" http://127.0.0.1:5000/api/upload


### Получение статистики

curl "http://127.0.0.1:5000/api/data/stats?file_id=1"


### Очистка данных (JSON)

curl "http://127.0.0.1:5000/api/data/clean?file_id=1&method=mean&format=json"

Доступные методы: `mean`, `median`, `drop`. Форматы: `json`, `csv`.

### Скачать очищенные данные в CSV

curl -O "http://127.0.0.1:5000/api/data/clean?file_id=1&method=median&format=csv"


### Построить график

curl "http://127.0.0.1:5000/api/data/plot?file_id=1&x=age&y=salary&type=scatter"

Типы: `scatter`, `hist`. Возвращается base64-изображение.

### Получить список всех файлов

curl "http://127.0.0.1:5000/api/files"


## Структура проекта


data_analyzer/
├── app/
│   ├── __init__.py      # Фабрика приложения
│   ├── models.py        # Модели SQLAlchemy
│   ├── routes.py        # Эндпоинты API
│   ├── services.py      # Бизнес-логика (Pandas, графики)
│   └── utils.py         # Вспомогательные функции
├── config.py            # Конфигурация (чтение .env)
├── run.py               # Точка входа
├── requirements.txt     # Зависимости
├── .env.example         # Шаблон переменных окружения
├── .gitignore           # Игнорируемые файлы
└── README.md            # Документация


## Обработка ошибок

HTTP статусы:
- `400` – отсутствуют обязательные параметры
- `404` – файл с указанным ID не найден
- `415` – неподдерживаемый формат файла
- `500` – внутренняя ошибка сервера

## Частые проблемы и решения

- **Ошибка подключения к PostgreSQL**: проверьте, запущен ли сервер, и правильность пароля в `.env`.
- **Команда `flask` не распознаётся**: используйте `python -m flask`.
- **Ошибка `ModuleNotFoundError`**: установите зависимости командой `pip install -r requirements.txt`.
- **Некорректные значения в статистике**: убедитесь, что в файле есть числовые колонки.
- **График не отображается**: декодируйте base64 через онлайн-конвертер.
