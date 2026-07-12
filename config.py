import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Central app configuration. All values are read from environment
    variables so secrets never live in source control. See .env.example
    for the variables you need to set.
    """

    # Flask session signing key — MUST be overridden in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "everlea")

    # ---- MySQL connection -------------------------------------------------
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "wedding_planner_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- Session / cookie hardening ---------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set SESSION_COOKIE_SECURE = True once the app is served over HTTPS.
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"

    PERMANENT_SESSION_LIFETIME_MINUTES = int(
        os.environ.get("SESSION_LIFETIME_MINUTES", "60")
    )
