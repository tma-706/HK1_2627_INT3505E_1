"""Minimal, testable Lost & Found REST API for Session 08 homework.

Run with: python -m app --port 5001

The matching implementation is deliberately deterministic and does not run
SigLIP2. It exists so Postman/Newman and Locust can test a realistic workflow.
"""

import argparse
import os
from functools import wraps
from pathlib import Path

from flask import Flask, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from matching import MODEL_VERSION, rank_candidates
from models import Claim, ItemPost, User, db


DEMO_USERS = (
    ("seeker@example.com", "seeker123", "Demo Seeker"),
    ("finder@example.com", "finder123", "Demo Finder"),
)


def create_app(config=None):
    project_dir = Path(__file__).resolve().parent
    instance_dir = project_dir / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    database_path = instance_dir / "lost_found.db"

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "lost-found-local-demo-secret"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TOKEN_MAX_AGE_SECONDS=24 * 60 * 60,
        JSON_SORT_KEYS=False,
        TESTING=False,
    )
    app.config.update(config or {})
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_demo_users()

    serializer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], salt="lost-found-auth"
    )

    def api_error(status, code, message, details=None):
        payload = {"code": code, "message": message}
        if details is not None:
            payload["details"] = details
        return jsonify(payload), status

    def issue_token(user):
        return serializer.dumps({"user_id": user.id})

    def require_auth(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            authorization = request.headers.get("Authorization", "")
            if not authorization.startswith("Bearer "):
                return api_error(401, "UNAUTHORIZED", "Bearer token is required")

            token = authorization.removeprefix("Bearer ").strip()
            try:
                payload = serializer.loads(
                    token, max_age=app.config["TOKEN_MAX_AGE_SECONDS"]
                )
            except SignatureExpired:
                return api_error(401, "TOKEN_EXPIRED", "Token has expired")
            except BadSignature:
                return api_error(401, "UNAUTHORIZED", "Invalid bearer token")

            user = db.session.get(User, payload.get("user_id"))
            if user is None or user.status != "ACTIVE":
                return api_error(401, "UNAUTHORIZED", "User is not active")
            g.current_user = user
            return view(*args, **kwargs)

        return wrapped

    def json_object():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else None

    def validate_post_payload(data):
        errors = {}
        for field in ("title", "description", "category", "location", "event_time"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                errors[field] = ["Field is required and must be a non-empty string."]

        image_urls = data.get("image_urls", [])
        if not isinstance(image_urls, list) or any(
            not isinstance(url, str) or not url.strip() for url in image_urls
        ):
            errors["image_urls"] = ["Must be a list of non-empty URL strings."]
        return errors

    def create_item_post(post_type):
        data = json_object()
        if data is None:
            return api_error(400, "INVALID_JSON", "Expected a JSON object")
        errors = validate_post_payload(data)
        if errors:
            return api_error(422, "VALIDATION_ERROR", "Invalid post data", errors)

        post = ItemPost(
            author_id=g.current_user.id,
            type=post_type,
            title=data["title"].strip(),
            description=data["description"].strip(),
            category=data["category"].strip(),
            location=data["location"].strip(),
            event_time=data["event_time"].strip(),
            image_urls=[url.strip() for url in data.get("image_urls", [])],
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict()), 201

    def get_post_or_error(post_id):
        post = db.session.get(ItemPost, post_id)
        if post is None:
            return None, api_error(404, "NOT_FOUND", "Post not found")
        return post, None

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="lost-found-api")

    @app.post("/api/v1/auth/login")
    def login():
        data = json_object()
        if data is None:
            return api_error(400, "INVALID_JSON", "Expected a JSON object")
        user = User.query.filter_by(email=data.get("email", "").casefold()).first()
        if user is None or not user.check_password(data.get("password", "")):
            return api_error(401, "INVALID_CREDENTIALS", "Invalid email or password")
        return jsonify(
            token=issue_token(user),
            token_type="Bearer",
            user={
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role,
            },
        )

    @app.post("/api/v1/lost-posts")
    @require_auth
    def create_lost_post():
        return create_item_post("LOST")

    @app.post("/api/v1/found-posts")
    @require_auth
    def create_found_post():
        return create_item_post("FOUND")

    @app.get("/api/v1/posts")
    @require_auth
    def list_posts():
        query = ItemPost.query.order_by(ItemPost.id)
        post_type = request.args.get("type")
        status = request.args.get("status")
        if post_type:
            post_type = post_type.upper()
            if post_type not in {"LOST", "FOUND"}:
                return api_error(422, "VALIDATION_ERROR", "type must be LOST or FOUND")
            query = query.filter_by(type=post_type)
        if status:
            query = query.filter_by(status=status.upper())
        return jsonify(items=[post.to_dict() for post in query.all()])

    @app.get("/api/v1/posts/<int:post_id>")
    @require_auth
    def get_post(post_id):
        post, error_response = get_post_or_error(post_id)
        if error_response:
            return error_response
        if post.status == "DRAFT" and post.author_id != g.current_user.id:
            return api_error(403, "FORBIDDEN", "Draft post is private")
        return jsonify(post.to_dict())

    @app.post("/api/v1/posts/<int:post_id>/publish")
    @require_auth
    def publish_post(post_id):
        post, error_response = get_post_or_error(post_id)
        if error_response:
            return error_response
        if post.author_id != g.current_user.id:
            return api_error(403, "FORBIDDEN", "Only the author can publish this post")
        if post.status != "DRAFT":
            return api_error(409, "INVALID_STATE", "Only a draft post can be published")
        if post.type == "FOUND" and not post.image_urls:
            return api_error(
                422,
                "IMAGE_REQUIRED",
                "A found post requires at least one completed image before publishing",
            )

        post.status = "PUBLISHED"
        post.matching_status = "QUEUED"
        db.session.commit()
        return jsonify(post.to_dict())

    @app.get("/api/v1/lost-posts/<int:post_id>/matches")
    @require_auth
    def lost_post_matches(post_id):
        post, error_response = get_post_or_error(post_id)
        if error_response:
            return error_response
        if post.type != "LOST":
            return api_error(422, "WRONG_POST_TYPE", "Expected a LOST post")
        if post.status != "PUBLISHED":
            return api_error(409, "POST_NOT_PUBLISHED", "Post must be published")

        try:
            limit = int(request.args.get("limit", "5"))
        except ValueError:
            return api_error(422, "VALIDATION_ERROR", "limit must be an integer")
        if not 1 <= limit <= 10:
            return api_error(422, "VALIDATION_ERROR", "limit must be between 1 and 10")

        candidates = ItemPost.query.filter_by(type="FOUND", status="PUBLISHED").all()
        items = rank_candidates(post, candidates, limit)
        post.matching_status = "READY"
        db.session.commit()
        return jsonify(
            query_post_id=post.id,
            count=len(items),
            limit=limit,
            model_version=MODEL_VERSION,
            items=items,
        )

    @app.post("/api/v1/found-posts/<int:found_post_id>/claims")
    @require_auth
    def create_claim(found_post_id):
        data = json_object()
        if data is None:
            return api_error(400, "INVALID_JSON", "Expected a JSON object")

        found_post, error_response = get_post_or_error(found_post_id)
        if error_response:
            return error_response
        lost_post = db.session.get(ItemPost, data.get("lost_post_id"))
        evidence = data.get("evidence")

        if found_post.type != "FOUND":
            return api_error(422, "WRONG_POST_TYPE", "Expected a FOUND post")
        if lost_post is None or lost_post.type != "LOST":
            return api_error(422, "INVALID_LOST_POST", "A valid LOST post is required")
        if lost_post.author_id != g.current_user.id:
            return api_error(403, "FORBIDDEN", "Claimant must own the lost post")
        if found_post.author_id == g.current_user.id:
            return api_error(422, "INVALID_CLAIM", "Cannot claim your own found post")
        if found_post.status != "PUBLISHED" or lost_post.status != "PUBLISHED":
            return api_error(409, "POST_NOT_ACTIVE", "Both posts must be published")
        if not isinstance(evidence, str) or not evidence.strip():
            return api_error(422, "EVIDENCE_REQUIRED", "Private evidence is required")

        claim = Claim(
            lost_post_id=lost_post.id,
            found_post_id=found_post.id,
            claimant_id=g.current_user.id,
            evidence=evidence.strip(),
        )
        db.session.add(claim)
        db.session.commit()
        return jsonify(claim.to_dict()), 201

    @app.get("/api/v1/claims/<int:claim_id>")
    @require_auth
    def get_claim(claim_id):
        claim = db.session.get(Claim, claim_id)
        if claim is None:
            return api_error(404, "NOT_FOUND", "Claim not found")
        if g.current_user.id not in {
            claim.claimant_id,
            claim.found_post.author_id,
        }:
            return api_error(403, "FORBIDDEN", "Claim evidence is private")
        return jsonify(claim.to_dict())

    return app


def _seed_demo_users():
    for email, password, display_name in DEMO_USERS:
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email, display_name=display_name)
            user.set_password(password)
            db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    create_app().run(host="127.0.0.1", port=args.port, debug=False)
