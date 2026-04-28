#!/bin/sh

# Останавливать выполнение, если любая команда завершилась ошибкой
set -e

echo "⌛ Ожидание запуска базы данных..."

# Магия: пытаемся подключиться к порту Postgres, пока он не ответит
# Мы используем python-код, так как в slim-образе может не быть утилиты nc или pg_isready
python << END
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.getenv("DATABASE_URL")
url = urlparse(db_url)
host = url.hostname
port = url.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        time.sleep(1)
END

echo "✅ База данных доступна!"

echo "🚀 Запуск миграций БД..."
alembic upgrade head

echo "🔥 Запуск приложения..."
# exec заменяет текущий процесс скрипта процессом uvicorn. 
# Это важно, чтобы Docker мог корректно останавливать контейнер (сигналы SIGTERM)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000