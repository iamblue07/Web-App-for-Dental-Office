import os
from dotenv import load_dotenv

load_dotenv()

# Scrie ca.pem din variabila de mediu daca exista
ca_cert = os.environ.get('CA_CERT')
if ca_cert:
    with open('ca.pem', 'w') as f:
        f.write(ca_cert.replace('\\n', '\n'))

_user = os.environ.get('MYSQL_USER')
_password = os.environ.get('MYSQL_PASSWORD')
_host = os.environ.get('MYSQL_HOST')
_port = os.environ.get('MYSQL_PORT', '3306')
_db = os.environ.get('MYSQL_DB')

_ssl = '?ssl_ca=ca.pem' if ca_cert else ''

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cheie-secreta-fallback'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_db}{_ssl}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024