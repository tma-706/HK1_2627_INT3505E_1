from flask import Flask, request, jsonify, make_response
from data import BOOKS
import hashlib
import json

app = Flask(__name__)

def find_by_id(book_id):
    return next((book for book in BOOKS if book['id'] == book_id), None)

def book_to_json(book):
    # lấy nội dung sách thành chuỗi JSON (json chứa trong string, ko phải mỗi json), không chứa trường etag
    content = {
        key: value
        for key, value in book.items()
        if key != "etag"
    }
    return json.dumps(
        content,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )

# Tính ETag từ nội dung JSON
def make_etag(book):
    content = book_to_json(book)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
# Tính Etag trước
for book in BOOKS:
    book["etag"] = make_etag(book)

@app.get("/books/<int:book_id>")
def fetch_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    etag = book["etag"]
    if request.if_none_match.contains_weak(etag):
        resp = make_response("", 304)
    else:
        resp = make_response(jsonify(book), 200)
        resp.headers["Content-Type"] = "application/json"
    resp.set_etag(etag)
    resp.headers["cache-control"] = "no-cache"
    return resp

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)