from flask import Flask, jsonify, request
from data import BOOKS_OPEN

_next = len(BOOKS_OPEN)

app = Flask(__name__)

def find_by_id(book_id):
    return next((book for book in BOOKS_OPEN if book['id'] == book_id), None)

@app.route("/books", methods=["GET"])
# (a) Dùng GET thêm query 
# (b) Dùng sort theo title, author, price
def list_books():
    limit = request.args.get('limit', 100, int)
    query_title = request.args.get('title', "").strip().lower() 
    query_author = request.args.get('author', "").strip().lower()
    sort = request.args.get('sort', "").strip().lower()
    books = [b for b in BOOKS_OPEN if query_title in b['title'].lower() and query_author in b['author'].lower()]
    if sort == "title":
        books.sort(key=lambda x: x['title'].lower())
    elif sort == "author":
        books.sort(key=lambda x: x['author'].lower())
    elif sort == "price":
        books.sort(key=lambda x: x['price'])
    return jsonify(books[:limit]), 200

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

# (c) check year >= 1900
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    author = data.get("author")
    genre = data.get("genre")
    price = data.get("price")
    year = data.get("year")
    if not title or not author or not genre or not price or not year:
        return jsonify({"error": "Missing required fields"}), 400
    if not isinstance(year, int) or year < 1900:
        return jsonify({"error": "Invalid year"}), 400
    _next += 1
    book = {
        "id": _next,
        "title": title,
        "author": author,
        "genre": genre,
        "price": price,
        "year": year
    }
    BOOKS_OPEN.append(book)
    return jsonify(book), 201, {"Location": f"/books/{_next}"}

@app.route("/books/<int:book_id>", methods=["PUT", "DELETE"])
def modify_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        author = data.get("author")
        genre = data.get("genre")
        price = data.get("price")
        year = data.get("year")
        for val in [title, author, genre]:
            if not isinstance(val, str) or not val.strip():
                return jsonify({"error": "Invalid data type"}), 400
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
            return jsonify({"error": "Invalid data type"}), 400
        if not isinstance(year, int) or year < 1900:
            return jsonify({"error": "Invalid year"}), 400
        book.clear()
        book.update({
            "id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "price": price,
            "year": year
        })
        return jsonify(book), 200
    BOOKS_OPEN.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
