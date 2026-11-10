import os
from pathlib import Path

INSTANCE_DIR = Path(
    os.environ.get(
        "INSTANCE_PATH",
        Path.cwd() / "instance",
    )
).resolve()

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