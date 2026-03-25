from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"  # for login session


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("students.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            age TEXT,
            course TEXT
        )
    """)
    return conn


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid Login"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
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
    data = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("index.html", students=data)


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
    conn.close()

    return redirect('/')


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- UPDATE ----------------
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        conn.execute("UPDATE students SET name=?, age=?, course=? WHERE id=?",
                     (name, age, course, id))
        conn.commit()
        conn.close()

        return redirect('/')

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("update.html", student=student)


# ---------------- SEARCH ----------------
@app.route('/search', methods=['POST'])
def search():
    if 'user' not in session:
        return redirect('/login')

    keyword = request.form['keyword']

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + keyword + '%',)
    ).fetchall()
    conn.close()

    return render_template("index.html", students=data)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    conn = get_db()  # ensures table is created
    conn.close()
    app.run(debug=True)
