from datetime import datetime, timezone
from email.utils import format_datetime
from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v1", __name__)
V1_SUNSET = datetime(
    2026,
    12,
    31,
    23,
    59,
    59,
    tzinfo=timezone.utc,
)

@bp.after_request
def add_sunset_header(response):
    response.headers["Sunset"] = format_datetime(
        V1_SUNSET,
        usegmt=True,
    )
    return response

@bp.route("/<int:uid>")
def get(uid):
    user = get_user(uid)
    if not user: return {"error": "not found"}, 404
    return {
        "id": uid,
        "full_name": f"{user['first_name']} {user['last_name']}",
        "email": user["email"],
    }
