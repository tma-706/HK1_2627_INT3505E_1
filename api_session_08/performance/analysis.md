# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 20 | 0.00% (0/143) | 4.96 |
| B | 50 | 5 | 60s | 26 | 0.07% (1/1362) | 23.08 |
| C | 200 | 50 | 30s | 170 | 0.14% (4/2790) | 94.52 |

## 1. Kịch bản có p95 cao nhất

Kịch bản C có p95 cao nhất, bằng 170 ms. Trong khi số user tăng từ 10 ở A
lên 50 ở B rồi 200 ở C, p95 tăng từ 20 ms lên 26 ms rồi 170 ms. RPS cũng
tăng từ 4.96 lên 23.08 rồi 94.52, nhưng độ trễ tăng mạnh ở kịch bản C. Kết
quả này cho thấy khi có 200 user ảo và spawn rate 50 user/giây, Flask
development server cùng SQLite phải xử lý nhiều request đồng thời hơn, làm
tăng thời gian chờ và tranh chấp tài nguyên.

## 2. Endpoint có failure rate tăng

Chỉ `GET /books?year=:year` có failure:

| Kịch bản | Requests | Failures | Failure rate của endpoint |
|---|---:|---:|---:|
| A | 21 | 0 | 0.00% |
| B | 189 | 1 | 0.53% |
| C | 415 | 4 | 0.96% |

Đây không phải HTTP 500 thật do Flask trả về. Code Locust chủ động gọi
`response.failure("Simulated 500: client-side injected failure")` với xác
suất 1%. Khi số request tăng, tỉ lệ quan sát tiến gần hơn tới 1%; sự tăng này
không chứng minh server bị lỗi do tải. Các endpoint khác có 0 failure trong
cả ba kịch bản. Ngoài ra, `GET /books/{id}` coi cả 200 và 404 là kết quả hợp
lệ nên 404 ngẫu nhiên không bị Locust tính là lỗi vận hành.

## 3. Đánh giá SLO p95 < 300 ms

Cả ba kịch bản đều đạt SLO giả định vì p95 tổng lần lượt là 20 ms, 26 ms và
170 ms, đều nhỏ hơn 300 ms. Ngay cả endpoint chậm nhất ở kịch bản C là
`POST /books` cũng có p95 bằng 250 ms.

Baseline đề xuất cho CI là kịch bản A: 10 user, spawn rate 2 user/giây trong
30 giây; pipeline chỉ pass khi p95 tổng nhỏ hơn 300 ms và không có HTTP 5xx
thật. Failure được chèn nhân tạo nên cần tách khỏi lỗi HTTP thật hoặc tắt cơ
chế chèn lỗi khi dùng bài test làm CI gate, tránh làm pipeline thất bại ngẫu
nhiên.

Kết quả này chỉ phản ánh một lần chạy trên máy cá nhân với Flask development
server và SQLite. Thời gian còn chịu ảnh hưởng của cấu hình máy, tiến trình
nền, dữ liệu tăng dần do task POST và tính ngẫu nhiên của Locust; vì vậy không
thể dùng trực tiếp để khẳng định hiệu năng production.

## 4. Trường hợp connection pool giới hạn 5

Nếu pool chỉ có 5 connection thì tối đa 5 thao tác cơ sở dữ liệu có thể mượn
connection cùng lúc; các request còn lại phải chờ connection được trả về.
Khi tải cao, p95/p99 có thể tăng, RPS có thể chững lại và có thể xuất hiện
timeout hoặc lỗi cạn pool.

Để kiểm chứng, cấu hình pool size bằng 5 rồi chạy lại cùng kịch bản C và so
sánh với report hiện tại. Cần quan sát p95/p99, RPS, failure/timeout trong
Locust và log SQLAlchemy ở server. Nếu số user tiếp tục tăng nhưng RPS không
tăng tương ứng, độ trễ tăng mạnh hoặc log xuất hiện timeout chờ connection,
đó là bằng chứng pool đã trở thành nút thắt.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.
