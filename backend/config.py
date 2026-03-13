"""TRAMPO v7 — Configurações"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY        = os.environ.get("SECRET_KEY", "trampo-secret-dev-2025")
    JWT_SECRET_KEY    = os.environ.get("JWT_SECRET_KEY", "trampo-jwt-dev-2025")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    SQLALCHEMY_DATABASE_URI  = os.environ.get("DATABASE_URL", "sqlite:///trampo.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    UPLOAD_FOLDER   = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    MAIL_USERNAME   = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD   = os.environ.get("MAIL_PASSWORD", "")

    STRIPE_SECRET_KEY      = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET  = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    OPENAI_API_KEY         = os.environ.get("OPENAI_API_KEY", "")
    GOOGLE_MAPS_API_KEY    = os.environ.get("GOOGLE_MAPS_API_KEY", "")

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


ActiveConfig = ProductionConfig if os.environ.get("FLASK_ENV") == "production" else DevelopmentConfig
