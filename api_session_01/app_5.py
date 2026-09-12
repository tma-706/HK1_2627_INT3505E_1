from flask import Flask, jsonify, request
from data import ORDERS

app = Flask(__name__)

@app.route('/orders/<id>', methods=['DELETE'])
def delete_order(id):
    order = ORDERS.get(id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    if order['status'] in ['shipped', 'delivered']:
        return jsonify({"error": "Cannot delete"}), 409
    del ORDERS[id]
    return "", 204

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)