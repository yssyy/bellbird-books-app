import os
class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "scu-isys3001-insecure-dev-key-change-in-prod")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "bellbird.db")
    DEBUG = (APP_ENV == "development")
