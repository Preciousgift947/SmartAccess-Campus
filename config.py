import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MYSQL_HOST = os.getenv('DB_HOST')
    MYSQL_USER = os.getenv('DB_USER')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
    MYSQL_DB = os.getenv('DB_NAME')
    MYSQL_PORT = int(os.getenv('DB_PORT', 3306))
    # Address phones use to reach this app, e.g. http://192.168.1.20:5000
    # Leave empty to use the address the student's browser is on.
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')
