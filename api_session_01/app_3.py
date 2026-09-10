from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

STUDENTS = []
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json(silent=False)
    name = data.get('name')
    gpa = data.get('gpa')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if not gpa:
        return jsonify({'error': 'GPA is required'}), 400
    student = {
        'id' : str(uuid4()),
        'name' : name,
        'gpa' : gpa,
    }
    STUDENTS.append(student)
    print(f"Student created: {student}, now we have {len(STUDENTS)} students")
    return student, 201

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)