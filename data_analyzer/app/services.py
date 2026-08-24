import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # отключает GUI-бэкенд, использует только рисование в буфер
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from flask import current_app
from app import db
from app.models import File, AnalysisResult

def save_file(filename, file_data):
    """
    Сохраняет загруженный файл в базу данных.
    """
    file_record = File(filename=filename, data=file_data)
    db.session.add(file_record)
    db.session.commit()
    return file_record

def read_dataframe(file_data, filename):
    """
    Преобразует байты файла в pandas DataFrame.
    """
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext == 'csv':
        return pd.read_csv(io.BytesIO(file_data))
    elif ext in ('xlsx', 'xls'):
        engine = 'openpyxl' if ext == 'xlsx' else 'xlrd'
        return pd.read_excel(io.BytesIO(file_data), engine=engine)
    else:
        raise ValueError('Неподдерживаемый формат файла')

def analyze_file(file_id):
    """
    Выполняет анализ данных и сохраняет статистику.
    Все numpy-типы преобразуются в стандартные Python-типы.
    """
    file_record = File.query.get(file_id)
    if not file_record:
        raise ValueError('Файл не найден')

    df = read_dataframe(file_record.data, file_record.filename)
    if df.empty:
        raise ValueError('Файл пуст или не содержит данных')

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if not numeric_cols:
        raise ValueError('Нет числовых колонок для анализа')

    stats = {}
    for col in numeric_cols:
        # Явно преобразуем numpy-типы в стандартные
        col_stats = {
            'mean': float(df[col].mean()),      # np.float64 -> float
            'median': float(df[col].median()),
            'count': int(df[col].count())       # np.int64 -> int
        }
        stats[col] = col_stats

    # Корреляционная матрица – преобразуем все значения в float
    corr_df = df[numeric_cols].corr()
    corr_matrix = {}
    for row in corr_df.index:
        corr_matrix[row] = {col: float(corr_df.loc[row, col]) for col in corr_df.columns}

    # Сохраняем в JSON-поле
    file_record.stats = {
        'column_stats': stats,
        'correlation': corr_matrix
    }
    db.session.commit()

    # Сохраняем в таблицу AnalysisResult (с преобразованием)
    for col, vals in stats.items():
        result = AnalysisResult(
            file_id=file_id,
            column_name=col,
            mean=vals['mean'],
            median=vals['median'],
            count=vals['count']
        )
        db.session.add(result)
    db.session.commit()

    return file_record.stats

def clean_data(file_id, method='mean'):
    """
    Очистка данных: удаление дубликатов и заполнение пропусков.
    """
    file_record = File.query.get(file_id)
    if not file_record:
        raise ValueError('Файл не найден')

    df = read_dataframe(file_record.data, file_record.filename)
    df = df.drop_duplicates()

    if method == 'drop':
        df = df.dropna()
    else:
        numeric_cols = df.select_dtypes(include='number').columns
        for col in numeric_cols:
            if method == 'mean':
                df[col].fillna(float(df[col].mean()), inplace=True)
            elif method == 'median':
                df[col].fillna(float(df[col].median()), inplace=True)

    return df

def generate_plot(file_id, x_col, y_col, plot_type='scatter'):
    """
    Генерирует график и возвращает его в base64.
    """
    file_record = File.query.get(file_id)
    if not file_record:
        raise ValueError('Файл не найден')

    df = read_dataframe(file_record.data, file_record.filename)
    if x_col not in df.columns or y_col not in df.columns:
        raise ValueError('Указанные колонки не найдены')

    sns.set_style('whitegrid')
    fig, ax = plt.subplots(figsize=(8, 6))

    if plot_type == 'scatter':
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
    elif plot_type == 'hist':
        df[[x_col, y_col]].hist(ax=ax)
    else:
        raise ValueError('Неподдерживаемый тип графика')

    ax.set_title(f'{plot_type.capitalize()} plot of {x_col} vs {y_col}')

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    img_buf.seek(0)

    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    return img_base64