"""Create repeatable published posts for Locust runs.

Run from the project root with: python -m scripts.seed_data
"""

from app import create_app
from models import ItemPost, User, db


FOUND_ITEMS = (
    (
        "Black backpack near library entrance",
        "Found a black backpack with a blue keychain near the entrance.",
        "BAG",
        "Main Library",
        "https://example.test/images/backpack-1.jpg",
    ),
    (
        "Dark laptop bag in reading room",
        "Found a dark laptop bag on the second floor.",
        "BAG",
        "Main Library",
        "https://example.test/images/laptop-bag.jpg",
    ),
    (
        "Blue water bottle",
        "Found a blue water bottle beside the library stairs.",
        "BOTTLE",
        "Main Library",
        "https://example.test/images/bottle.jpg",
    ),
    (
        "Black backpack at sports hall",
        "Found a black backpack after the evening practice.",
        "BAG",
        "Sports Hall",
        "https://example.test/images/backpack-2.jpg",
    ),
    (
        "Brown wallet",
        "Found a brown wallet near the cafeteria.",
        "WALLET",
        "Cafeteria",
        "https://example.test/images/wallet.jpg",
    ),
)


def ensure_post(author, post_type, title, description, category, location, images):
    post = ItemPost.query.filter_by(author_id=author.id, title=title).first()
    if post is None:
        post = ItemPost(
            author_id=author.id,
            type=post_type,
            title=title,
            description=description,
            category=category,
            location=location,
            event_time="2026-11-16T10:00:00+07:00",
            image_urls=images,
            status="PUBLISHED",
            matching_status="READY",
        )
        db.session.add(post)
    else:
        post.status = "PUBLISHED"
        post.matching_status = "READY"
    return post


def main():
    app = create_app()
    with app.app_context():
        seeker = User.query.filter_by(email="seeker@example.com").one()
        finder = User.query.filter_by(email="finder@example.com").one()

        lost = ensure_post(
            seeker,
            "LOST",
            "Load test lost black backpack",
            "Lost a black backpack with a blue keychain near the library.",
            "BAG",
            "Main Library",
            [],
        )

        for title, description, category, location, image_url in FOUND_ITEMS:
            ensure_post(
                finder,
                "FOUND",
                title,
                description,
                category,
                location,
                [image_url],
            )

        db.session.commit()
        print(f"Seed complete. Published LOST post id: {lost.id}")


if __name__ == "__main__":
    main()
