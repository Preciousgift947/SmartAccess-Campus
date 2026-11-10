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

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800

    @classmethod
    def validate_config(cls):
        required = [
            cls.SECRET_KEY,
            cls.MYSQL_HOST,
            cls.MYSQL_USER,
            cls.MYSQL_PASSWORD,
            cls.MYSQL_DB
        ]

        if not all(required):
            raise RuntimeError(
                "Missing required application configuration."
            )
