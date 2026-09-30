from flask import Flask, jsonify, request
from data import POSTS

app = Flask(__name__)
next_post_id = max((post["id"] for post in POSTS), default=0)

@app.get("/posts")
def list_post():
    return jsonify({
        "data": POSTS,
        "total": len(POSTS)
    }), 200

@app.post("/posts")
def create_post():
    global next_post_id
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="invalid JSON"), 400

    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")
    if (
        not isinstance(title, str) or not title.strip()
        or not isinstance(content, str) or not content.strip()
        or isinstance(author_id, bool) or not isinstance(author_id, int)
        or author_id <= 0
    ):
        return jsonify({
            "error": "title and content must be non-empty strings; author_id must be a positive integer"
        }), 422

    next_post_id += 1
    post = {
        "id": next_post_id,
        "title": title.strip(),
        "content": content.strip(),
        "author_id": author_id
    }
    POSTS.append(post)
    return jsonify(post), 201, {"Location": f"/posts/{next_post_id}"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

