from pathlib import Path
from flask import Flask, jsonify
from .config import Config, INSTANCE_DIR
from .errors import register_error_handlers
from .extensions import db, migrate

def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_path=str(INSTANCE_DIR),
        instance_relative_config=True,
    )
    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    db.init_app(app)
    migrate.init_app(app, db)

    # Nạp model để Flask-Migrate nhìn thấy metadata.
    from . import models  # noqa: F401
    from .api import health_bp, orders_bp, products_bp
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    register_error_handlers(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "product-api",
                "status": "ok",
            }
        ), 200
    return app