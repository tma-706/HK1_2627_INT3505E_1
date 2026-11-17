"""Database models for the minimal Lost & Found testing slice."""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="USER")
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ItemPost(db.Model):
    __tablename__ = "item_posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    event_time = db.Column(db.String(40), nullable=False)
    image_urls = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(20), nullable=False, default="DRAFT", index=True)
    matching_status = db.Column(
        db.String(20), nullable=False, default="NOT_INDEXED"
    )
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    author = db.relationship(User, lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "location": self.location,
            "event_time": self.event_time,
            "image_urls": list(self.image_urls or []),
            "status": self.status,
            "matching_status": self.matching_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    lost_post_id = db.Column(
        db.Integer, db.ForeignKey("item_posts.id"), nullable=False
    )
    found_post_id = db.Column(
        db.Integer, db.ForeignKey("item_posts.id"), nullable=False
    )
    claimant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    evidence = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="PENDING")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    lost_post = db.relationship(ItemPost, foreign_keys=[lost_post_id], lazy="joined")
    found_post = db.relationship(ItemPost, foreign_keys=[found_post_id], lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "lost_post_id": self.lost_post_id,
            "found_post_id": self.found_post_id,
            "claimant_id": self.claimant_id,
            "evidence": self.evidence,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
