import logging
from datetime import datetime, timezone
from flask import Flask
from sunset import deprecate_at

logging.basicConfig(level=logging.WARNING)
app = Flask(__name__)
V1_SUNSET = datetime(
    2026,
    12,
    31,
    23,
    59,
    59,
    tzinfo=timezone.utc,
)
USERS = {
    1: {
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn",
    }
}

@app.route("/api/v1/users/<int:uid>")
@deprecate_at(
    V1_SUNSET,
    replacement="/api/v2/users",
)
def get_user_v1(uid):
    user = USERS.get(uid)
    if not user:
        return {"error": "not found"}, 404
    return {
        "id": uid,
        "full_name": (
            f"{user['first_name']} "
            f"{user['last_name']}"
        ),
    }

@app.route("/api/v2/users/<int:uid>")
def get_user_v2(uid):
    user = USERS.get(uid)
    if not user:
        return {"error": "not found"}, 404
    return {
        "id": uid,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }

if __name__ == "__main__":
    app.run(debug=True)