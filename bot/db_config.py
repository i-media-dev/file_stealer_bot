import os

from dotenv import load_dotenv

load_dotenv()

"""
Конфигурационные параметры для подключения к PostgreSQL базе данных.

Содержит настройки подключения, которые загружаются из переменных окружения:
- user (логин)
- password (пароль)
- host (хост)
- database (название базы данных)
- port (порт по умолчанию 3306)
- connection_timeout (таймаут подключения)
- use_pure (флаг использования чистого Python-коннектора)

Пример переменных окружения:
LOGIN='admin'
PASSWORD='secret'
HOST='db.example.com'
DB_NAME='production_db'
"""
config = {
    'user': os.getenv('DB_LOGIN_CARMONEY'),
    'password': os.getenv('DB_PASSWORD_CARMONEY'),
    'host': os.getenv('DB_HOST_CARMONEY'),
    'database': os.getenv('DB_NAME_CARMONEY'),
    'port': os.getenv('DB_PORT_CARMONEY', 6432),
    'connect_timeout': 10
}
