from functools import wraps

from flask import Flask, jsonify, request


app = Flask(__name__)

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}

USERS = {
    1: {
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn",
    }
}


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            version = request.headers.get(
                "X-API-Version",
                default,
            )

            if version not in supported:
                return jsonify(
                    error="unsupported version",
                    supported=sorted(supported),
                ), 400

            result = function(version, *args, **kwargs)

            if isinstance(result, tuple):
                body, status = result
            else:
                body, status = result, 200

            response = jsonify(body)
            response.status_code = status
            response.headers["X-API-Version-Served"] = version

            return response

        return wrapper

    return decorate


@app.route("/users/<int:uid>", methods=["GET"])
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)

    if not user:
        return {"error": "not found"}, 404

    if version == "1":
        return {
            "id": uid,
            "full_name": (
                f"{user['first_name']} "
                f"{user['last_name']}"
            ),
        }

    # Version 2 và version theo ngày dùng schema mới.
    return {
        "id": uid,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }


if __name__ == "__main__":
    app.run(debug=True)