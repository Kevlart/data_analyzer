import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Config:
    # Секретный ключ для подписей сессий и защиты
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Строка подключения к PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:12345@localhost:5432/data_analyzer'
    )

    # Отключаем отслеживание изменений объектов (для производительности)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Максимальный размер загружаемого файла (16 МБ)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Допустимые расширения файлов
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}