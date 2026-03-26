from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("students.db", check_same_thread=False)


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        age INTEGER,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        course TEXT
    )
    """)

    # Default Admin
    admin = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not admin:
        conn.execute("""
        INSERT INTO users(name,email,phone,age,username,password,role)
        VALUES ('Admin','admin@gmail.com','9999999999',25,'admin','admin','admin')
        """)

    conn.commit()


init_db()


# ---------- ROUTES ----------

@app.route('/')
def home():
    return redirect('/login')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        ).fetchone()

        if user:
            session['user'] = user[5]
            session['role'] = user[7]

            if user[7] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/user')

    return render_template("login.html")


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['age'],
            request.form['username'],
            request.form['password'],
            'user'
        )

        conn = get_db()
        conn.execute("""
        INSERT INTO users(name,email,phone,age,username,password,role)
        VALUES(?,?,?,?,?,?,?)
        """, data)
        conn.commit()

        return redirect('/login')

    return render_template("signup.html")


# ADMIN PANEL
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    students = conn.execute("SELECT * FROM students").fetchall()

    return render_template("admin.html", users=users, students=students)


# USER DASHBOARD
@app.route('/user')
def user():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()

    return render_template("user_dashboard.html", students=students)


# ADD STUDENT
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    course = request.form['course']

    conn = get_db()
    conn.execute("INSERT INTO students(name,course) VALUES(?,?)", (name, course))
    conn.commit()

    return redirect('/user')


# DELETE (ADMIN ONLY)
@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()

    return redirect('/admin')


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
