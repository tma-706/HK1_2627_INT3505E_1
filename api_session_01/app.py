from flask import Flask, jsonify, request
#Do flask 3.x.x đã tự chuyển dict sang json nên không cần jsonify, ở đây chỉ thêm để phân biệt

app = Flask(__name__)

#GET
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

#POST
@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"You sent": data}), 200
    
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)