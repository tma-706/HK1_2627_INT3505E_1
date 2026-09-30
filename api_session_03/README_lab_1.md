# Lab 1 — Thiết kế resource cho Blog API

## 1. Bài toán và phạm vi

Blog cho phép người dùng đăng bài viết, bình luận vào bài viết, gắn thẻ cho bài viết, xem hồ sơ người dùng và theo dõi người dùng khác.

Theo đề bài, lab này cần: xác định resource; phân loại collection, item và sub-resource; vẽ cây endpoint và chọn cách đánh phiên bản API; sau đó triển khai Flask routes cho **collection `/posts`**. Các endpoint còn lại là **bản thiết kế**, chưa bắt buộc viết code trong `lab_1.py`.

## 2. Resource và quan hệ

| Resource | Ý nghĩa | Quan hệ |
| --- | --- | --- |
| `users` | Người dùng và hồ sơ | Một user có thể viết nhiều post và theo dõi nhiều user khác |
| `posts` | Bài viết | Thuộc về một user; có nhiều comment và tag |
| `comments` | Bình luận | Thuộc về một post và do một user viết |
| `tags` | Thẻ phân loại bài viết | Một tag có thể gắn với nhiều post |
| `following` | Quan hệ theo dõi | Một user theo dõi một user khác |

## 3. Phân loại collection / item / sub-resource

Các đường dẫn dùng danh từ số nhiều, chữ thường. `{user_id}`, `{post_id}`, `{comment_id}` và `{tag_id}` là ID của resource tương ứng.

### Collection

```text
/users
/posts
/tags
```

### Item

```text
/users/{user_id}
/posts/{post_id}
/tags/{tag_id}
```

### Sub-resource

```text
/users/{user_id}/following
/users/{user_id}/followers
/users/{user_id}/posts
/posts/{post_id}/comments
/posts/{post_id}/comments/{comment_id}
/posts/{post_id}/tags
/posts/{post_id}/tags/{tag_id}
```

**Version segment:** Lab này không thêm tiền tố phiên bản, nên URL bắt đầu trực tiếp bằng `/users`, `/posts` hoặc `/tags`, đúng như danh sách trên. Nếu sau này cần nhiều phiên bản API, có thể thêm `/api/v1` ở đầu các đường dẫn.

## 4. Cây endpoint

```text
/
├── users
│   └── {user_id}
│       ├── following
│       ├── followers
│       └── posts
├── posts
│   └── {post_id}
│       ├── comments
│       │   └── {comment_id}
│       └── tags
│           └── {tag_id}
└── tags
    └── {tag_id}
```

## 5. Các API dự kiến

### Resource `users`

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| `GET` | `/users` | Lấy danh sách người dùng |
| `POST` | `/users` | Tạo người dùng |
| `GET` | `/users/{user_id}` | Xem hồ sơ người dùng |
| `PATCH` | `/users/{user_id}` | Cập nhật hồ sơ |
| `GET` | `/users/{user_id}/following` | Xem những người user đang theo dõi |
| `POST` | `/users/{user_id}/following` | Theo dõi người dùng có `target_user_id` trong JSON body |
| `GET` | `/users/{user_id}/followers` | Xem những người đang theo dõi user |
| `GET` | `/users/{user_id}/posts` | Lấy các bài viết của user |

### Resource `posts`

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| `GET` | `/posts` | Lấy danh sách bài viết |
| `POST` | `/posts` | Tạo bài viết |
| `GET` | `/posts/{post_id}` | Xem một bài viết |
| `PATCH` | `/posts/{post_id}` | Sửa bài viết |
| `DELETE` | `/posts/{post_id}` | Xóa bài viết |
| `GET` | `/posts/{post_id}/comments` | Lấy bình luận của bài viết |
| `POST` | `/posts/{post_id}/comments` | Thêm bình luận vào bài viết |
| `GET` | `/posts/{post_id}/comments/{comment_id}` | Xem một bình luận |
| `PATCH` | `/posts/{post_id}/comments/{comment_id}` | Sửa bình luận |
| `DELETE` | `/posts/{post_id}/comments/{comment_id}` | Xóa bình luận |
| `GET` | `/posts/{post_id}/tags` | Xem các thẻ của bài viết |
| `PUT` | `/posts/{post_id}/tags/{tag_id}` | Gắn thẻ vào bài viết |
| `DELETE` | `/posts/{post_id}/tags/{tag_id}` | Gỡ thẻ khỏi bài viết |

### Resource `tags`

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| `GET` | `/tags` | Lấy danh sách thẻ |
| `POST` | `/tags` | Tạo thẻ |
| `GET` | `/tags/{tag_id}` | Xem một thẻ |

## 6. Phần cần triển khai bằng Flask trong lab

Triển khai hai route cho collection `/posts` trong [lab_1.py](lab_1.py):

| Method | Kết quả mong đợi | Status khi thành công |
| --- | --- | --- |
| `GET /posts` | Trả về JSON chứa danh sách bài viết | `200 OK` |
| `POST /posts` | Nhận JSON, tạo bài viết và trả về bài vừa tạo | `201 Created` |
