from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age TEXT,
            course TEXT
        )
    """)
    conn.commit()
    conn.close()

# 🔥 IMPORTANT FIX (RUN ALWAYS - FOR RENDER)
init_db()

# ---------------- LOGIN ----------------
stored_username = "admin"
stored_password = generate_password_hash("1234")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == stored_username and check_password_hash(stored_password, password):
            session['user'] = username
            return redirect('/')
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------- HOME ----------------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    return render_template("index.html", students=students)

# ---------------- ADD ----------------
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    age = request.form['age']
    course = request.form['course']

    conn = get_db()
    conn.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
                 (name, age, course))
    conn.commit()

    return redirect('/')

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

# ---------------- UPDATE ----------------
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        conn.execute("UPDATE students SET name=?, age=?, course=? WHERE id=?",
                     (name, age, course, id))
        conn.commit()
        return redirect('/')

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    return render_template("update.html", student=student)

# ---------------- SEARCH ----------------
@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + keyword + '%',)
    ).fetchall()

    return render_template("index.html", students=data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
