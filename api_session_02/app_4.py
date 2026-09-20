from flask import Flask, jsonify
from pathlib import Path
from contextlib import closing
import sqlite3

app = Flask(__name__)

#file DB cùng thư mục
DB_PATH = Path(__file__).resolve().parent / "orders.db"
# __file__ lấy đường dẫn đến file hiện tại (có thể chưa được chuẩn hóa)
# resolve giúp chuẩn hóa đường dẫn

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Cho phép đọc các cột bằng tên, ví dụ order["status"], nếu ko thì phải đọc bằng vị trí (phải nhớ số) do fetchone() trả về tuple, nếu có sqlite3.Row thì fetchone() trả về đối tượng sqlite3.Row nên có thể gọi bằng tên cột
    return conn

def init_db():
    with closing(connect_db()) as conn:
    # mở kết nối bằng connect_db(), dùng nó trong khối with, rồi tự đóng khi rời khối, kể cả khi có lỗi; không tự commit()
    # conn là đối tượng kết nối tới database, dùng để thực thi SQL và quản lý transaction; kết nối được tự động đóng khi rời khối with
        table_exists = conn.execute(
            "SELECT name from sqlite_master "
            "WHERE type = 'table' AND name = 'orders'"
        ).fetchone()
        # kiểm tra xem bảng tồn tại ko, nếu có thì trả về 1 hàng, ko thì None
        if table_exists is not None:
            return
        
        conn.execute("""
            CREATE TABLE orders (
                id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                book_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                status TEXT NOT NULL
            )
        """)
        #  """...""" chuỗi nhiều dòng trong python
        # conn.executemany(cau_sql, danh_sach_cac_tuple_gia_tri)
        conn.executemany(
            """
            INSERT INTO orders (id, customer, book_id, quantity, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("1", "An", 1, 1, "pending"),
                ("2", "Binh", 3, 2, "processing"),
                ("3", "Chi", 5, 1, "shipped"),
                ("4", "Dung", 7, 1, "delivered")
            ]
        )
        conn.commit() #commit lên DB
    
@app.get("/orders/<oid>")
def get_order(oid):
    with closing(connect_db()) as conn:
        # conn.execute(cau_sql, tuple_gia_tri)
        order = conn.execute(
            "SELECT * FROM orders WHERE orders.id = ?",
            (oid,)
        ).fetchone()
        # Dùng ? và tuple tham số để truyền giá trị Python vào SQL.
    # Nếu viết thẳng tên oid trong chuỗi SQL, SQLite hiểu đó là tên cột.

    if order is None:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(dict(order)), 200

@app.route('/orders/<oid>', methods=['DELETE'])
def delete_order(oid):
    with closing(connect_db()) as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE orders.id = ?",
            (oid,)
        ).fetchone()
        if order is None:
            return jsonify({"error": "Order not found"}), 404
        if order['status'] in ['shipped', 'delivered']:
            return jsonify({"error": "Cannot delete"}), 409
        conn.execute(
            "DELETE FROM orders WHERE orders.id = ?",
            (oid,)
        )
        conn.commit()
    return "", 204

if __name__ == '__main__':
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)