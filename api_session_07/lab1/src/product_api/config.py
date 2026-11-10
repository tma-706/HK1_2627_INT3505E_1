import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSTANCE_DIR = PROJECT_ROOT / "instance"

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key",
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DB_URL",
        "sqlite:///products.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False