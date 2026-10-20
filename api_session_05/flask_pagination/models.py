from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )

    books: Mapped[list["Book"]] = relationship(
        back_populates="author"
    )


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    genre: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    price: Mapped[int] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id"),
        nullable=False
    )

    author: Mapped["Author"] = relationship(
        back_populates="books"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": {
                "id": self.author.id,
                "name": self.author.name
            },
            "genre": self.genre,
            "price": self.price,
            "created_at": self.created_at.isoformat()
        }