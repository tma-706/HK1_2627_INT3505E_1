from flask import Flask, jsonify, request

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Romance"
    }
]
_next_id = len(BOOKS)

@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify({
            "error": "Unexpected JSON" 
        }), 415
    data = request.get_json(silent = True) or {}
    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    genre = data.get("genre", "").strip()
    if not title or not author or not genre:
        return jsonify({
            "error": "Empty fields"
        }), 422
    _next_id += 1
    book = {
        "id": _next_id,
        "title": title,
        "author": author,
        "genre": genre,
    }
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{_next_id}"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
