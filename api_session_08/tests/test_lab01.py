"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import pytest
from jsonschema import ValidationError, validate

from tools import get_book_schema

def test_get_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_unknown_book(client):
    response = client.get("/books/999")
    body = response.get_json(silent=True)
    assert response.status_code == 404
    assert body["code"] == "NOT_FOUND"

def test_post_only_author(client):
    response = client.post(
        "/books",
        json={
            "author": "Hihi",
        },
    )
    body = response.get_json()
    assert response.status_code == 400
    assert any(
        error["field"] == "title" for error in body["errors"]
    )

def test_deleted_book_cannot_be_fetched(client):
    create_response = client.post(
        "/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "year": 2008,
            "isbn": "9780132350884",
        },
    )
    assert create_response.status_code == 201
    created_book = create_response.get_json()
    book_id = created_book["id"]

    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204
    assert delete_response.data == b""

    get_response = client.get(f"/books/{book_id}")
    body = get_response.get_json()
    assert get_response.status_code == 404
    assert body["code"] == "NOT_FOUND"

def test_response_extra_field_blocked(client, sample_book):
    response = client.get(f"/books/{sample_book}")
    assert response.status_code == 200
    original_body = response.get_json()
    modified_body = original_body.copy()
    modified_body["password_hash"] = "secret"

    assert "password_hash" not in original_body
    assert "password_hash" in modified_body
    schema = get_book_schema()
    with pytest.raises(ValidationError) as exc_info:
        validate(
            instance=modified_body,
            schema=schema,
        )
    assert exc_info.value.validator == "additionalProperties"
    assert "password_hash" in exc_info.value.message