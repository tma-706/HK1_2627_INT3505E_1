from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

class ProblemError(Exception):
    def __init__(self, status_code, title, detail, type_ = "about:blank"):
        super().__init__(detail)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type = type_

def problem_response(status_code, title, detail, type_ = "about:blank"):
    return jsonify({
        "type": type_,
        "title": title,
        "detail": detail,
        "status": status_code,
        "instance": request.path
    })
    response.status_code = status_code
    response.content_type = "application/problem+json"
    return response

@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return problem_response(
        error.status_code, error.title, error.detail, error.type
    )

@app.errorhandler(HTTPException)
def handle_http(error):
    return problem_response(
        error.code, error.name, error.description
    )

@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    app.logger.exception("Unhandled error")
    return problem_response(
        500, "Internal Server Error", "An unexpected error occurred."
    )

@app.get("/books/<book_id>")
def get_book(book_id):
    book_id = int(book_id)
    if book_id <= 0:
        raise ProblemError(
            400,
            "Invalid Book ID",
            "Book ID must be a positive integer."
        )
    return jsonify({"id": book_id, "title": "Sample Book", "author": "Sample Author"})

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)