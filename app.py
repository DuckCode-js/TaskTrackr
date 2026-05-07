from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
import sys
import os
from functools import wraps
import json

# Resolve base path — differs when running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    _base = sys._MEIPASS
    _data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'TaskTrackr')
    os.makedirs(_data_dir, exist_ok=True)
    DB = os.path.join(_data_dir, 'tasktrackr.db')
    app = Flask(__name__,
                template_folder=os.path.join(_base, 'templates'),
                static_folder=os.path.join(_base, 'static'))
else:
    DB = 'tasktrackr.db'
    app = Flask(__name__)

app.secret_key = 'tasktrackr-dev-secret-2026'  # change before deploying to production


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        due_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    try:
        conn.execute('ALTER TABLE tasks ADD COLUMN due_date TEXT')
    except Exception:
        pass  # column already exists
    conn.commit()
    conn.close()


init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    total = len(tasks)
    done = sum(1 for t in tasks if t['completed'])
    pct = int(done / total * 100) if total else 0
    ring_offset = round(339 * (1 - done / total)) if total else 339
    return render_template('dashboard.html', total=total, done=done, pending=total - done,
                           pct=pct, ring_offset=ring_offset)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            conn.commit()
            conn.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken', 'error')
    return render_template('register.html')


@app.route('/tasks')
@login_required
def tasks():
    conn = get_db()
    task_list = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? ORDER BY completed ASC, id DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('tasks.html', tasks=task_list)


@app.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '').strip() or None
    if title:
        conn = get_db()
        conn.execute('INSERT INTO tasks (user_id, title, due_date) VALUES (?, ?, ?)',
                     (session['user_id'], title, due_date))
        conn.commit()
        conn.close()
    return redirect(url_for('tasks'))


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    conn = get_db()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, session['user_id'])
    ).fetchone()
    if task:
        conn.execute('UPDATE tasks SET completed = ? WHERE id = ?',
                     (0 if task['completed'] else 1, task_id))
        conn.commit()
    conn.close()
    return redirect(url_for('tasks'))


@app.route('/tasks/<int:task_id>/edit', methods=['POST'])
@login_required
def edit_task(task_id):
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '').strip() or None
    if title:
        conn = get_db()
        conn.execute('UPDATE tasks SET title = ?, due_date = ? WHERE id = ? AND user_id = ?',
                     (title, due_date, task_id, session['user_id']))
        conn.commit()
        conn.close()
    return redirect(url_for('tasks'))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    conn = get_db()
    conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?',
                 (task_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('tasks'))


@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    task_count = conn.execute(
        'SELECT COUNT(*) FROM tasks WHERE user_id = ?', (session['user_id'],)
    ).fetchone()[0]
    done_count = conn.execute(
        'SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 1', (session['user_id'],)
    ).fetchone()[0]
    conn.close()
    return render_template('profile.html', task_count=task_count, done_count=done_count)


@app.route('/calendar')
@login_required
def calendar():
    conn = get_db()
    task_list = conn.execute(
        'SELECT id, title, due_date, completed FROM tasks WHERE user_id = ? AND due_date IS NOT NULL ORDER BY due_date',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    tasks_json = json.dumps([dict(t) for t in task_list])
    return render_template('calendar.html', tasks_json=tasks_json)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
