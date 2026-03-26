from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("/tmp/app.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            age TEXT,
            password TEXT,
            role TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            course TEXT
        )
    """)

    conn.commit()

    # CREATE DEFAULT ADMIN
    admin = conn.execute("SELECT * FROM users WHERE email='admin@gmail.com'").fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users (name,email,phone,age,password,role) VALUES (?,?,?,?,?,?)",
            ("Admin", "admin@gmail.com", "9999999999", "25",
             generate_password_hash("admin123"), "admin")
        )
        conn.commit()

    conn.close()

init_db()

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        age = request.form['age']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name,email,phone,age,password,role) VALUES (?,?,?,?,?,?)",
                (name, email, phone, age, password, "user")
            )
            conn.commit()
            flash("Signup successful!", "success")
            return redirect('/login')
        except:
            flash("Email already exists!", "danger")

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']

            if user['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            flash("Invalid login!", "danger")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- USER DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM students WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    return render_template("user_dashboard.html", data=data)

# ---------------- ADD DATA ----------------
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')

    name = request.form['name']
    course = request.form['course']

    conn = get_db()
    conn.execute(
        "INSERT INTO students (user_id,name,course) VALUES (?,?,?)",
        (session['user_id'], name, course)
    )
    conn.commit()

    flash("Data added!", "success")
    return redirect('/dashboard')

# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    students = conn.execute("SELECT * FROM students").fetchall()

    return render_template("admin.html", users=users, students=students)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()

    return redirect('/admin')

if __name__ == "__main__":
    app.run(debug=True)
