import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'cineworld-secret-2025')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_PORT = os.getenv('DB_PORT', '5432')
    SESSION_TYPE = 'cookie'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True