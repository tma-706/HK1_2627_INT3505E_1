import base64
import binascii
import json
from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import and_, func, or_, select

from models import Author, Book, db


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

SORTABLE_FIELDS = {
    "id": Book.id,
    "title": Book.title,
    "price": Book.price,
    "created_at": Book.created_at
}

def seed_data():
    number_of_books = db.session.scalar(
        select(func.count()).select_from(Book)
    )

    if number_of_books > 0:
        return

    robert = Author(name="Robert C. Martin")
    david = Author(name="David Thomas")
    eric = Author(name="Eric Matthes")
    miguel = Author(name="Miguel Grinberg")
    tolkien = Author(name="J. R. R. Tolkien")
    rowling = Author(name="J. K. Rowling")
    george_martin = Author(name="George R. R. Martin")
    frank = Author(name="Frank Herbert")
    asimov = Author(name="Isaac Asimov")
    orwell = Author(name="George Orwell")
    murakami = Author(name="Haruki Murakami")

    books = [
        Book(
            title="Clean Code",
            author=robert,
            genre="technology",
            price=250000,
            created_at=datetime(2025, 1, 1)
        ),
        Book(
            title="The Pragmatic Programmer",
            author=david,
            genre="technology",
            price=280000,
            created_at=datetime(2025, 1, 2)
        ),
        Book(
            title="Python Crash Course",
            author=eric,
            genre="technology",
            price=250000,
            created_at=datetime(2025, 1, 3)
        ),
        Book(
            title="Flask Web Development",
            author=miguel,
            genre="technology",
            price=220000,
            created_at=datetime(2025, 1, 4)
        ),
        Book(
            title="The Hobbit",
            author=tolkien,
            genre="fantasy",
            price=180000,
            created_at=datetime(2025, 1, 5)
        ),
        Book(
            title="Harry Potter",
            author=rowling,
            genre="fantasy",
            price=200000,
            created_at=datetime(2025, 1, 6)
        ),
        Book(
            title="A Game of Thrones",
            author=george_martin,
            genre="fantasy",
            price=230000,
            created_at=datetime(2025, 1, 7)
        ),
        Book(
            title="Dune",
            author=frank,
            genre="science-fiction",
            price=230000,
            created_at=datetime(2025, 1, 8)
        ),
        Book(
            title="Foundation",
            author=asimov,
            genre="science-fiction",
            price=190000,
            created_at=datetime(2025, 1, 9)
        ),
        Book(
            title="1984",
            author=orwell,
            genre="fiction",
            price=150000,
            created_at=datetime(2025, 1, 10)
        ),
        Book(
            title="Animal Farm",
            author=orwell,
            genre="fiction",
            price=120000,
            created_at=datetime(2025, 1, 11)
        ),
        Book(
            title="Norwegian Wood",
            author=murakami,
            genre="romance",
            price=170000,
            created_at=datetime(2025, 1, 12)
        )
    ]

    db.session.add_all(books)
    db.session.commit()
def parse_sort(sort_value):
    if not sort_value:
        raise ValueError("Sort value is required")
    
    sort_parts = [
        part.strip() for part in sort_value.split(",")
    ]
    if any(not part for part in sort_parts):
        raise ValueError("Sort value contains empty fields")

    parsed_sort = []
    used_fields = set()

    for part in sort_parts:
        descending = part.startswith("-")
        field_name = part[1:] if descending else part
        if field_name not in SORTABLE_FIELDS:
            raise ValueError(f"Invalid sort field: {field_name}")
        if field_name in used_fields:
            raise ValueError(f"Duplicate sort field: {field_name}")
        used_fields.add(field_name)
        parsed_sort.append((field_name, descending))
    if "id" not in used_fields:
        parsed_sort.append(("id", False))
    return parsed_sort

def encode_cursor(book, parsed_sort, sort_signature, genre):
    values = []
    for field_name, _ in parsed_sort:
        value = getattr(book, field_name)
        if isinstance(value, datetime):
            value = value.isoformat()
        values.append(value)
    cursor_data = {
        "sort": sort_signature,
        "genre": genre,
        "values": values
    }
    cursor_json = json.dumps(
        cursor_data,
        ensure_ascii=False
    )
    cursor_bytes = base64.urlsafe_b64encode(
        cursor_json.encode("utf-8")
    )
    return cursor_bytes.decode("ascii")

def decode_cursor(cursor_text):
    try:
        cursor_bytes = base64.b64decode(
            cursor_text.encode("ascii"),
            altchars=b"-_",
            validate=True
        )
        cursor_json = cursor_bytes.decode("utf-8")
        cursor_data = json.loads(cursor_json)
        if not isinstance(cursor_data, dict):
            raise ValueError()
        if "sort" not in cursor_data:
            raise ValueError()
        if "genre" not in cursor_data:
            raise ValueError()
        if "values" not in cursor_data:
            raise ValueError()
        if not isinstance(cursor_data["values"], list):
            raise ValueError()
        return cursor_data
    except (
        ValueError,
        TypeError,
        UnicodeError,
        binascii.Error
    ):
        return None

@app.get("/books")
def list_books():
    strategy = request.args.get("strategy", "offset").strip().lower()
    if strategy not in ("offset", "cursor"):
        return jsonify({"error": "Invalid pagination strategy"}), 400
    offset_value = request.args.get("offset", 0)
    limit_value = request.args.get("limit", 10)
    try:
        offset = int(offset_value)
        limit = int(limit_value)
    except ValueError:
        return jsonify({"error": "Invalid offset or limit values"}), 400
    if offset < 0:
        return jsonify({"error": "Offset must be non-negative"}), 400
    if limit <= 0 or limit > 100:
        return jsonify({"error": "Limit must be a positive integer between 1 and 100"}), 400

    genre = request.args.get("genre")
    sort_value = request.args.get("sort", "id").strip()
    try:
        parsed_sort = parse_sort(sort_value)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    sort_signature = ",".join(
        f"-{field_name}" if descending else field_name
        for field_name, descending in parsed_sort
    )
    order_by_expressions = []
    for sort_item in parsed_sort:
        field_name, descending = sort_item
        column = SORTABLE_FIELDS[field_name]
        order_by_expressions.append(column.desc() if descending else column.asc())

    book_statement = select(Book)
    if genre:
        book_statement = book_statement.where(
            Book.genre == genre
        )
    # CURSOR PAGINATION
    if strategy == "cursor":
        cursor_text = request.args.get("cursor")

        if cursor_text:
            cursor_data = decode_cursor(
                cursor_text
            )
            if cursor_data is None:
                return jsonify({"error": "invalid_cursor"}), 400
            if cursor_data["sort"] != sort_signature:
                return jsonify({
                    "error": "cursor_sort_mismatch"}), 400
            if cursor_data["genre"] != genre:
                return jsonify({
                    "error": "cursor_filter_mismatch",
                }), 400
            cursor_values = cursor_data["values"]
            if len(cursor_values) != len(parsed_sort):
                return jsonify({
                    "error": "invalid_cursor"
                }), 400
            converted_values = []
            try:
                for index, sort_item in enumerate(parsed_sort):
                    field_name, _ = sort_item
                    value = cursor_values[index]
                    if field_name in {"id", "price"}:
                        if isinstance(value, bool):
                            raise ValueError()
                        value = int(value)
                    elif field_name == "created_at":
                        if not isinstance(value, str):
                            raise ValueError()
                        value = datetime.fromisoformat(
                            value
                        )
                    elif field_name == "title":
                        if not isinstance(value, str):
                            raise ValueError()
                    else:
                        raise ValueError()
                    converted_values.append(value)
            except (ValueError, TypeError):
                return jsonify({
                    "error": "invalid_cursor"
                }), 400

            cursor_conditions = []
            equal_conditions = []

            for index, sort_item in enumerate(parsed_sort):
                field_name, descending = sort_item
                column = SORTABLE_FIELDS[field_name]
                value = converted_values[index]
                if descending:
                    comparison = column < value
                else:
                    comparison = column > value
                cursor_conditions.append(
                    and_(
                        *equal_conditions,
                        comparison
                    )
                )
                equal_conditions.append(
                    column == value
                )
            book_statement = book_statement.where(
                or_(*cursor_conditions)
            )
        statement = (
            book_statement
            .order_by(*order_by_expressions)
            .limit(limit + 1)
        )
        books = db.session.scalars(
            statement
        ).all()
        has_more = len(books) > limit
        page = books[:limit]
        if has_more:
            next_cursor = encode_cursor(
                page[-1],
                parsed_sort,
                sort_signature,
                genre
            )
        else:
            next_cursor = None

        return jsonify({
            "data": [
                book.to_dict()
                for book in page
            ],
            "pagination": {
                "strategy": "cursor",
                "limit": limit,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "sort": sort_value
            }
        }), 200


    # OFFSET PAGINATION
    count_statement = (
        select(func.count())
        .select_from(Book)
    )
    if genre:
        count_statement = count_statement.where(
            Book.genre == genre
        )
    total = db.session.scalar(
        count_statement
    )
    statement = (
        book_statement
        .order_by(*order_by_expressions)
        .offset(offset)
        .limit(limit)
    )
    books = db.session.scalars(
        statement
    ).all()
    has_next = offset + len(books) < total

    return jsonify({
        "data": [
            book.to_dict()
            for book in books
        ],
        "pagination": {
            "strategy": "offset",
            "offset": offset,
            "limit": limit,
            "total": total,
            "has_next": has_next,
            "sort": sort_value
        }
    }), 200

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)