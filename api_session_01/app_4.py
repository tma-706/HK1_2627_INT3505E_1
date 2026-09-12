from flask import Flask, jsonify, request
from data import BOOKS

app = Flask(__name__)

def find_by_id(book_id):
    return next((book for book in BOOKS if book['id'] == book_id), None)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
      return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200 

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return jsonify({"item_id": item_id}), 200

@app.route('/books', methods=['GET'])
def list_books():
    limit = request.args.get('limit', default=20, type=int)
    # Có thể viết limit = request.args.get('limit', 20), giống lệnh req.query.limit trong expressjs và khai báo tham số trong fastapi
    query_title = request.args.get('title', "").strip().lower() 
    query_author = request.args.get('author', "").strip().lower()
    if query_title == "" and query_author == "":
        return jsonify(BOOKS[:limit]), 200
    elif query_title == "":
        books = [b for b in BOOKS if query_author in b['author'].lower()]
    elif query_author == "":
        books = [b for b in BOOKS if query_title in b['title'].lower()]
    else:   
        books = [b for b in BOOKS if query_title in b['title'].lower() and query_author in b['author'].lower()]
    return jsonify(books[:limit]), 200

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)