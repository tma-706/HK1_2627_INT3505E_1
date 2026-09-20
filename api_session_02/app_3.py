from flask import Flask, jsonify, request, make_response
from urllib.parse import urlencode
from data import BOOKS

app = Flask(__name__)

DEFAULT_SIZE, MAX_SIZE = 20, 100

@app.get("/books")
def list_books():
    try:
        size = int(request.args.get("size", DEFAULT_SIZE))
        page = int(request.args.get("page", 1))
    except ValueError:
        return jsonify({"error": "Size and page must be integers"}), 400
    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)
    # filter (app_6_open.py)
    flt = BOOKS
    author = request.args.get("author", "").strip()
    if author:
        flt = [book for book in flt if author.lower() in book["author"].lower()]
    title = request.args.get("title", "").strip()
    if title:
        flt = [book for book in flt if title.lower() in book["title"].lower()]  
    genre = request.args.get("genre", "").strip()
    if genre:
        flt = [book for book in flt if genre.lower() in book["genre"].lower()]
    #pagination
    total = len(flt)
    start = (page - 1) * size
    end = start + size
    data = flt[start:end]
    total_pages = (total + size - 1) // size
    # HATEOS links
    def make_link(page):
        params = {
            "page": page,
            "size": size
        }
        if author:
            params["author"] = author
        if title:
            params["title"] = title
        if genre:
            params["genre"] = genre
        return "/books?" + urlencode(params)

    links = {
        "self": {"href": make_link(page)},
        "first": {"href": make_link(1)},
        "last": {"href": make_link(total_pages)}
    }
    if page > 1:
        links["prev"] = {"href": make_link(page - 1)}
    if page < total:
        links["next"] = {"href": make_link(page + 1)}
    body = {
        "data": data,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_page": total_pages
        },
        "_links": links
    }    
    response = make_response(jsonify(body), 200)
    response.headers["Cache-Control"] = "public, max-age=30"
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)