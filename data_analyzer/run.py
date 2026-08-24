from app import create_app

# Создаём экземпляр приложения
app = create_app()

if __name__ == '__main__':
    # Запускаем сервер. debug=True включает автоматическую перезагрузку при изменениях.
    app.run(host='0.0.0.0', port=5000, debug=True)