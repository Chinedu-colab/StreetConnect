import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'streetconnect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False