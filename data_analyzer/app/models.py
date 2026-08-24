from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

# Модель для хранения загруженных файлов
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)          # Уникальный идентификатор
    filename = db.Column(db.String(255), nullable=False)  # Имя файла
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)  # Время загрузки
    data = db.Column(db.LargeBinary, nullable=False)      # Содержимое файла (байты)
    stats = db.Column(JSON, nullable=True)                # Результаты анализа (JSON)

    # Связь с таблицей результатов анализа (один-ко-многим)
    analysis_results = db.relationship('AnalysisResult', backref='file', lazy=True)

# Модель для хранения результатов анализа по каждой колонке
class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    mean = db.Column(db.Float)      # Среднее
    median = db.Column(db.Float)    # Медиана
    count = db.Column(db.Integer)   # Количество непустых значений