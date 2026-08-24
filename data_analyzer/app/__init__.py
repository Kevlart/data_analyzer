from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Инициализируем объекты расширений без привязки к приложению
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    # Создаём экземпляр Flask
    app = Flask(__name__)

    # Загружаем конфигурацию
    app.config.from_object(config_class)

    # Связываем расширения с приложением
    db.init_app(app)
    migrate.init_app(app, db)

    # Импортируем и регистрируем Blueprint с API-эндпоинтами
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app