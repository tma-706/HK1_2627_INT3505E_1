from flask import Blueprint, request
from .users_data import get_user, create_user
bp = Blueprint("v2", __name__)
@bp.route("/<int:uid>")
def get(uid):
    user = get_user(uid)
    if not user: return {"error": "not found"}, 404
    return {
        "id": uid,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }

@bp.route("", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    required_fields = ("first_name", "last_name", "email")
    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]
    if missing_fields:
        return {
            "error": "missing required fields",
            "fields": missing_fields,
        }, 400
    uid, user = create_user(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
    )
    return {
        "id": uid,
        **user,
    }, 201