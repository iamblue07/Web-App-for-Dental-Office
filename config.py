import os
from dotenv import load_dotenv

load_dotenv()

_user = os.environ.get('MYSQL_USER')
_password = os.environ.get('MYSQL_PASSWORD')
_host = os.environ.get('MYSQL_HOST')
_port = os.environ.get('MYSQL_PORT', '3306')
_db = os.environ.get('MYSQL_DB')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cheie-secreta-fallback'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024