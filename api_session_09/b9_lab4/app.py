from flask import Flask, jsonify, request
from gateway import dispatch

app = Flask(__name__)

@app.route("/orders", methods=["POST"])
def create_order():
    body = request.get_json(silent=True) or {}
    if not body.get("account_id"):
        return {
            "error": "account_id is required",
        }, 400
    handler, result = dispatch(body)
    response = jsonify(result)
    response.headers["X-Order-Handler"] = handler
    if handler == "v2":
        return response, 201
    return response, 200

if __name__ == "__main__":
    app.run(debug=True)