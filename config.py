import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'bank.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail (Gmail SMTP example - use an "App Password", not your real Gmail password)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    # App security rules
    OTP_EXPIRY_MINUTES = 10
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=30)
