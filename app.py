from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("students.db")

# 🔍 SEARCH
@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + keyword + '%',)
    ).fetchall()

    return render_template("index.html", students=data)

# 🏠 HOME
@app.route('/')
def index():
    conn = get_db()
    data = conn.execute("SELECT * FROM students").fetchall()
    return render_template("index.html", students=data)

# ➕ ADD
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    age = request.form['age']
    course = request.form['course']

    conn = get_db()
    conn.execute(
        "INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
        (name, age, course)
    )
    conn.commit()

    return redirect('/')

# 🗑️ DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

# ✏️ UPDATE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        conn.execute(
            "UPDATE students SET name=?, age=?, course=? WHERE id=?",
            (name, age, course, id)
        )
        conn.commit()
        return redirect('/')

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    return render_template("update.html", student=student)

# 🔥 MAIN RUN
if __name__ == "__main__":
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            age TEXT,
            course TEXT
        )
    """)
    conn.close()

    app.run(debug=True)