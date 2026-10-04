"""Dữ liệu bài viết mẫu cho Blog API của lab 1."""

POSTS = [
    {
        "id": 1,
        "title": "Bài viết đầu tiên",
        "content": "Chào mừng đến với blog của mình.",
        "author_id": 1,
    },
    {
        "id": 2,
        "title": "Học Flask cơ bản",
        "content": "Flask giúp tạo API đơn giản bằng Python.",
        "author_id": 1,
    },
    {
        "id": 3,
        "title": "Thiết kế REST API",
        "content": "Sử dụng resource và HTTP method để tổ chức endpoint.",
        "author_id": 2,
    },
]


ORDERS = [
    {
        "id": 1,
        "customer_id": 101,
        "status": "paid",
        "total": 120000,
        "created_at": "2026-10-01T09:00:00Z",
    },
    {
        "id": 2,
        "customer_id": 102,
        "status": "pending",
        "total": 250000,
        "created_at": "2026-10-01T10:00:00Z",
    },
    {
        "id": 3,
        "customer_id": 101,
        "status": "paid",
        "total": 80000,
        "created_at": "2026-10-02T08:30:00Z",
    },
    {
        "id": 4,
        "customer_id": 103,
        "status": "cancelled",
        "total": 310000,
        "created_at": "2026-10-02T11:00:00Z",
    },
    {
        "id": 5,
        "customer_id": 102,
        "status": "paid",
        "total": 175000,
        "created_at": "2026-10-03T09:15:00Z",
    },
    {
        "id": 6,
        "customer_id": 101,
        "status": "pending",
        "total": 90000,
        "created_at": "2026-10-03T14:00:00Z",
    },
    {
        "id": 7,
        "customer_id": 104,
        "status": "paid",
        "total": 420000,
        "created_at": "2026-10-04T08:00:00Z",
    },
    {
        "id": 8,
        "customer_id": 103,
        "status": "paid",
        "total": 150000,
        "created_at": "2026-10-04T10:00:00Z",
    },
]