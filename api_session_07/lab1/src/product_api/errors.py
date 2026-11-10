from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from .extensions import db

class ApiError(Exception):
    status_code = 500
    error = "internal_error"
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail

class NotFoundError(ApiError):
    status_code = 404
    error = "not_found"

class ConflictError(ApiError):
    status_code = 409
    error = "conflict"

class OutOfStockError(ApiError):
    status_code = 409
    error = "out_of_stock"

def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(exc):
        return jsonify(
            {
                "error": exc.error,
                "detail": exc.detail,
            }
        ), exc.status_code
    @app.errorhandler(ValidationError)
    def handle_validation_error(exc):
        return jsonify(
            {
                "error": "validation_error",
                "detail": exc.messages,
            }
        ), 422
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        error_name = exc.name.lower().replace(" ", "_")
        return jsonify(
            {
                "error": error_name,
                "detail": exc.description,
            }
        ), exc.code
    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        db.session.rollback()
        app.logger.exception("unhandled exception")
        return jsonify(
            {
                "error": "internal_error",
                "detail": "an unexpected error occurred",
            }
        ), 500