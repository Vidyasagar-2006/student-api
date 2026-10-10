from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
DB = "students.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        course TEXT NOT NULL)""")
    conn.commit()
    conn.close()

@app.post("/students")
def create_student():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("email") or not data.get("course"):
        return jsonify({"error": "name, email and course are required"}), 400
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO students(name, email, course) VALUES(?, ?, ?)",
        (data["name"], data["email"], data["course"])
    )
    conn.commit()
    student_id = cur.lastrowid
    conn.close()
    return jsonify({"message": "Student created successfully", "student_id": student_id}), 201

@app.get("/students")
def get_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.get("/students/<int:id>")
def get_student(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(row))

@app.put("/students/<int:id>")
def update_student(id):
    data = request.get_json() or {}
    conn = get_db()
    cur = conn.execute(
        "UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?",
        (data.get("name"), data.get("email"), data.get("course"), id)
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student updated successfully"})

@app.delete("/students/<int:id>")
def delete_student(id):
    conn = get_db()
    cur = conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted successfully"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)