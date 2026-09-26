import os
import re
import secrets
import sqlite3
import time
from datetime import timedelta
from functools import wraps

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")

# ---------- Cơ sở dữ liệu (SQLite) ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# ---------- Giới hạn số lần đăng nhập sai ----------
MAX_ATTEMPTS = 5
LOCK_SECONDS = 15 * 60
failed_attempts = {}  # username -> {"count": int, "locked_until": float}


def is_locked(username):
    entry = failed_attempts.get(username)
    return bool(entry and entry["locked_until"] > time.time())


def record_failure(username):
    entry = failed_attempts.setdefault(username, {"count": 0, "locked_until": 0})
    entry["count"] += 1
    if entry["count"] >= MAX_ATTEMPTS:
        entry["locked_until"] = time.time() + LOCK_SECONDS
        entry["count"] = 0


# ---------- Chống CSRF ----------
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get("csrf_token")
        if not token or token != request.form.get("csrf_token"):
            abort(400, "CSRF token không hợp lệ.")


@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return {"csrf_token": session["csrf_token"]}


# ---------- Decorator ----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# ---------- Route ----------
@app.route("/")
def index():
    return redirect(url_for("dashboard" if "username" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        error = None
        if not USERNAME_RE.match(username):
            error = "Tên đăng nhập phải từ 3-20 ký tự (chữ, số, dấu gạch dưới)."
        elif len(password) < 6:
            error = "Mật khẩu phải có ít nhất 6 ký tự."
        elif password != confirm:
            error = "Mật khẩu xác nhận không khớp."

        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = "Tên đăng nhập đã tồn tại."
            else:
                flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                return redirect(url_for("login"))

        flash(error, "error")
        return render_template("register.html", username=username)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Vui lòng nhập tên đăng nhập và mật khẩu.", "error")
        elif is_locked(username):
            flash("Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.", "error")
        else:
            user = get_db().execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user is None or not check_password_hash(user["password_hash"], password):
                record_failure(username)
                flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
            else:
                failed_attempts.pop(username, None)
                # Xoá session cũ để tránh session fixation
                session.clear()
                session.permanent = True
                session["username"] = user["username"]
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("dashboard"))

        return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))
