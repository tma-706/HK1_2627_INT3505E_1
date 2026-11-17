# Lost & Found Matching API — Load-test Analysis

## Phạm vi và SLO đề xuất

Endpoint chính được kiểm thử:

```http
GET /api/v1/lost-posts/{id}/matches?limit=5|10
```

SLO đề xuất cho bản demo:

- p95 của endpoint matching nhỏ hơn **300 ms**.
- Tỉ lệ HTTP 5xx nhỏ hơn **1%**.
- Tỉ lệ request thành công đạt ít nhất **99%**.

Các số liệu trong bảng chỉ lấy dòng `GET /api/v1/lost-posts/{id}/matches`
trong report Locust. Request đăng nhập và lấy danh sách bài ở `on_start` là bước
chuẩn bị dữ liệu cho mỗi user, không được gộp vào p95 của endpoint chính.

## Cách chạy

Môi trường thử nghiệm là Flask development server và SQLite trên một máy local.
Dữ liệu được tạo trước bằng `python -m scripts.seed_data`. Mỗi virtual user đăng
nhập, lấy danh sách Lost Post đã publish, sau đó liên tục gọi endpoint matching
với `limit` được chọn ngẫu nhiên giữa 5 và 10.

## Kết quả

| Scenario | Users | Spawn rate | Duration | Requests | p95 | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A — baseline | 10 | 2 user/s | 30s | 260 | 24 ms | 0% | 9.21 |
| B — normal load | 50 | 5 user/s | 60s | 2,685 | 48 ms | 0% | 45.26 |
| C — spike | 200 | 50 user/s | 30s | 2,378 | 2,600 ms | 0% | 80.85 |

Report chi tiết: [A.html](../reports/A.html), [B.html](../reports/B.html) và
[C.html](../reports/C.html).

## Phân tích

Scenario A và B đạt toàn bộ SLO đề xuất. Khi tăng từ 10 lên 50 user, throughput
tăng gần tuyến tính từ 9.21 lên 45.26 RPS, trong khi p95 chỉ tăng từ 24 lên 48
ms. Điều này cho thấy hệ thống local còn đủ khả năng phục vụ mức tải 50 user.

Scenario C không đạt SLO latency. Khi số user tăng từ 50 lên 200 (gấp 4), RPS
chỉ tăng từ 45.26 lên 80.85 (khoảng 1.79 lần), nhưng p95 tăng từ 48 lên 2,600
ms (hơn 54 lần). Đây là dấu hiệu throughput bắt đầu bão hòa: request vẫn thành
công nhưng phải xếp hàng lâu, nên failure rate 0% không có nghĩa là hệ thống
vẫn đáp ứng tốt.

Với môi trường demo hiện tại, ngưỡng vận hành hợp lý là tối đa khoảng 50 virtual
user đồng thời và p95 dưới 300 ms. Scenario C được xem là spike vượt khả năng
của cấu hình local. Nếu dùng trong production cần chạy lại với WSGI server,
PostgreSQL, connection pool và hạ tầng gần với triển khai thật trước khi chốt
SLO chính thức.

## Hạn chế

Test này dùng thuật toán matching giả lập theo từ khóa/category/location trên
Flask development server và SQLite. Nó chưa đo thời gian suy luận AI, RabbitMQ,
vector search, MinIO/S3, moderation, notification hoặc hệ thống phân tán. Vì
vậy SLO trên chỉ là quality gate cho bản demo, không phải cam kết production.
