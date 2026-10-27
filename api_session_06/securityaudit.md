# Security Audit

## Phạm vi

Audit ba endpoint:

- POST /auth/login
- POST /auth/refresh
- GET /posts/{id}

## Các điểm có thể lộ

1. Account enumeration tại login
   - Email không tồn tại và mật khẩu sai có thể trả message hoặc thời gian phản hồi khác nhau.
   - Kiểm soát: cùng status 401, cùng lỗi `invalid_credentials`, giảm chênh lệch thời gian xử lý.

2. Credential stuffing và brute force
   - Login không có rate limit cho phép thử nhiều mật khẩu.
   - Kiểm soát: rate limit theo IP và account, cảnh báo bất thường; tránh lockout vĩnh viễn gây denial of service.

3. Password hoặc token xuất hiện trong log
   - Request body, Authorization header hoặc response token có thể bị log.
   - Kiểm soát: redact password/token, chỉ log user ID, event và request ID.

4. JWT làm lộ dữ liệu trong payload
   - JWT ký không mã hóa payload; PII và secret có thể bị đọc.
   - Kiểm soát: chỉ lưu sub, jti, roles/scopes cần thiết; không đặt password,
     email nhạy cảm hoặc secret trong claims.

5. Token bị đánh cắp qua localStorage/XSS
   - JavaScript độc hại có thể đọc access và refresh token.
   - Kiểm soát: cân nhắc BFF hoặc cookie HttpOnly, Secure, SameSite; vẫn phải
     chống CSRF và XSS.

6. Refresh token sống lâu nhưng không rotate/revoke
   - Refresh token bị đánh cắp có thể được tái sử dụng lâu dài.
   - Kiểm soát: refresh rotation, lưu session/jti, phát hiện reuse và revoke
     cả token family.

7. BOLA tại GET /posts/{id}
   - User đổi id để đọc private post của người khác.
   - Kiểm soát: sau khi kiểm access token và `posts:read`, tiếp tục kiểm
     visibility, owner, follower/share relationship và tenant.



