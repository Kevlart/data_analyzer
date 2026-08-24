from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.services import save_file, analyze_file, clean_data, generate_plot
from app.models import File
from app import db
import io
import pandas as pd

# Создаём Blueprint для группировки маршрутов
api_bp = Blueprint('api', __name__)

def allowed_file(filename):
    """
    Проверяет, разрешено ли расширение файла.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Эндпоинт для загрузки файла
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Ожидает multipart/form-data с полем 'file'.
    Возвращает ID загруженного файла и автоматически запускает анализ.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не передан'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Неподдерживаемый тип файла. Разрешены: csv, xlsx, xls'}), 415

    # Безопасное имя файла (убираем опасные символы)
    filename = secure_filename(file.filename)
    file_data = file.read()

    try:
        # Сохраняем файл в БД
        file_record = save_file(filename, file_data)
        # Автоматически выполняем анализ
        analyze_file(file_record.id)
        return jsonify({
            'message': 'Файл успешно загружен и проанализирован',
            'file_id': file_record.id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Эндпоинт для получения статистики
@api_bp.route('/data/stats', methods=['GET'])
def get_stats():
    """
    Возвращает статистику по указанному файлу.
    Параметр file_id (если не указан, берётся последний загруженный).
    """
    file_id = request.args.get('file_id')
    if file_id is None:
        # Берём последний загруженный файл (по убыванию id)
        file_record = File.query.order_by(File.id.desc()).first()
        if not file_record:
            return jsonify({'error': 'Нет загруженных файлов'}), 404
        file_id = file_record.id

    file_record = File.query.get(file_id)
    if not file_record:
        return jsonify({'error': 'Файл не найден'}), 404

    if not file_record.stats:
        return jsonify({'error': 'Статистика для этого файла ещё не вычислена'}), 404

    return jsonify({
        'file_id': file_record.id,
        'filename': file_record.filename,
        'stats': file_record.stats
    }), 200

# Эндпоинт для очистки данных
@api_bp.route('/data/clean', methods=['GET'])
def clean():
    """
    Очищает данные: удаляет дубликаты и заполняет пропуски.
    Параметры:
      - file_id (обязательный)
      - method: mean (по умолчанию), median или drop
      - format: json (по умолчанию) или csv – формат ответа
    """
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': 'Необходимо указать file_id'}), 400

    method = request.args.get('method', 'mean')
    if method not in ('mean', 'median', 'drop'):
        return jsonify({'error': 'Недопустимый метод. Используйте mean, median или drop'}), 400

    format_type = request.args.get('format', 'json').lower()
    if format_type not in ('json', 'csv'):
        return jsonify({'error': 'Недопустимый формат. Используйте json или csv'}), 400

    try:
        df_cleaned = clean_data(int(file_id), method)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Ошибка очистки: {str(e)}'}), 500

    if format_type == 'csv':
        # Возвращаем CSV-файл для скачивания
        csv_data = df_cleaned.to_csv(index=False)
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='cleaned_data.csv'
        )
    else:
        # Возвращаем JSON-массив объектов
        return jsonify(df_cleaned.to_dict(orient='records')), 200

# Эндпоинт для построения графика (продвинутый уровень)
@api_bp.route('/data/plot', methods=['GET'])
def plot():
    """
    Строит график (scatter или histogram) и возвращает изображение в base64.
    Параметры:
      - file_id (обязательный)
      - x: колонка для оси X
      - y: колонка для оси Y
      - type: scatter (по умолчанию) или hist
    """
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': 'Необходимо указать file_id'}), 400

    x_col = request.args.get('x')
    y_col = request.args.get('y')
    if not x_col or not y_col:
        return jsonify({'error': 'Необходимо указать x и y колонки'}), 400

    plot_type = request.args.get('type', 'scatter')
    if plot_type not in ('scatter', 'hist'):
        return jsonify({'error': 'Недопустимый тип графика. Используйте scatter или hist'}), 400

    try:
        img_base64 = generate_plot(int(file_id), x_col, y_col, plot_type)
        return jsonify({
            'plot': img_base64,
            'format': 'png_base64'
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Ошибка построения графика: {str(e)}'}), 500

# Дополнительный эндпоинт для получения списка всех загруженных файлов
@api_bp.route('/files', methods=['GET'])
def list_files():
    """
    Возвращает список всех файлов с их ID, именем и временем загрузки.
    """
    files = File.query.order_by(File.id.desc()).all()
    return jsonify([{
        'id': f.id,
        'filename': f.filename,
        'upload_time': f.upload_time.isoformat(),
        'has_stats': bool(f.stats)
    } for f in files]), 200