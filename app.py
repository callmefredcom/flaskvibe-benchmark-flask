import os
import psycopg2
import psycopg2.extras
import bcrypt
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/benchmark_flask')


def db():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def login_required(f):
    @wraps(f)
    def w(*a, **kw):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*a, **kw)
    return w


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with db() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (request.form['email'],))
            u = cur.fetchone()
        if u and bcrypt.checkpw(request.form['password'].encode(), u['password_hash'].encode()):
            session['user_id'] = u['id']
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pw = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt()).decode()
        with db() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (request.form['email'], pw))
        flash('Account created — please log in')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Dashboard (public — Lighthouse benchmarks this route) ─────────────────────

@app.route('/dashboard')
def dashboard():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM projects")
        total = cur.fetchone()['n']
        cur.execute("SELECT COUNT(*) AS n FROM projects WHERE status = 'active'")
        active = cur.fetchone()['n']
        cur.execute("SELECT COUNT(*) AS n FROM projects WHERE status = 'completed'")
        done = cur.fetchone()['n']
        cur.execute("SELECT COALESCE(SUM(budget), 0) AS s FROM projects")
        budget = cur.fetchone()['s']
        cur.execute("""
            SELECT id, title, status, budget, created_at
            FROM projects ORDER BY created_at DESC LIMIT 10
        """)
        recent = cur.fetchall()
    return render_template('dashboard.html', total=total, active=active, done=done, budget=budget, recent=recent)


# ── Projects (auth required) ───────────────────────────────────────────────────

@app.route('/projects')
@login_required
def projects():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    per = 20
    offset = (page - 1) * per
    like = f'%{q}%'
    with db() as conn, conn.cursor() as cur:
        if q:
            cur.execute("SELECT COUNT(*) AS n FROM projects WHERE title ILIKE %s OR description ILIKE %s", (like, like))
            total = cur.fetchone()['n']
            cur.execute("""
                SELECT id, title, status, budget, created_at FROM projects
                WHERE title ILIKE %s OR description ILIKE %s
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """, (like, like, per, offset))
        else:
            cur.execute("SELECT COUNT(*) AS n FROM projects")
            total = cur.fetchone()['n']
            cur.execute("""
                SELECT id, title, status, budget, created_at FROM projects
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """, (per, offset))
        rows = cur.fetchall()
    return render_template('projects.html', rows=rows, page=page, pages=(total + per - 1) // per, total=total, q=q)


@app.route('/projects/<int:pid>')
@login_required
def project(pid):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM projects WHERE id = %s", (pid,))
        p = cur.fetchone()
    if not p:
        return redirect(url_for('projects'))
    return render_template('project.html', p=p)


@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        with db() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (user_id, title, description, budget, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                session['user_id'],
                request.form['title'],
                request.form.get('description', ''),
                request.form.get('budget') or 0,
                request.form.get('status', 'active'),
            ))
        return redirect(url_for('projects'))
    return render_template('new_project.html')


if __name__ == '__main__':
    app.run(debug=True)
