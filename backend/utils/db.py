"""utils/db.py — Railway Cloud MySQL database layer for DIP Learning Simulator.

Performance: Uses a 5-connection pool (MySQLConnectionPool) to avoid the ~200 ms
TCP handshake overhead on every query.  The pool is lazily initialised once and
reused across all requests / Streamlit reruns.
"""
import hashlib
import os
import threading
from datetime import datetime

try:
    import streamlit as st
except ImportError:
    st = None  # allow import outside Streamlit (FastAPI context)

try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# ── Load Railway connection config ────────────────────────────────────────────
# Priority: Streamlit secrets → environment variables → fallback prompt
def _get_cfg():
    """Get MySQL config from st.secrets or environment variables."""
    try:
        s = st.secrets["mysql"]
        return {
            "host":     s["host"],
            "port":     int(s.get("port", 3306)),
            "database": s["database"],
            "user":     s["user"],
            "password": s["password"],
        }
    except Exception:
        pass
    # Fall back to env vars (Railway auto-injects these)
    return {
        "host":     os.environ.get("MYSQLHOST",     ""),
        "port":     int(os.environ.get("MYSQLPORT", 3306)),
        "database": os.environ.get("MYSQLDATABASE", "railway"),
        "user":     os.environ.get("MYSQLUSER",     "root"),
        "password": os.environ.get("MYSQLPASSWORD", ""),
    }


# ── Connection pool (one pool shared across all threads) ─────────────────────
_pool: "mysql.connector.pooling.MySQLConnectionPool | None" = None
_pool_lock = threading.Lock()


def _get_pool():
    """Lazily create and return the shared connection pool (5 connections)."""
    global _pool
    if _pool is not None:
        return _pool
    if not MYSQL_AVAILABLE:
        raise RuntimeError("mysql-connector-python not installed.")
    cfg = _get_cfg()
    if not cfg["host"]:
        raise RuntimeError("MySQL host not configured. Set credentials in .streamlit/secrets.toml")
    with _pool_lock:
        if _pool is None:  # double-checked locking
            _pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="dip_pool",
                pool_size=5,
                pool_reset_session=True,
                host=cfg["host"],
                port=cfg["port"],
                database=cfg["database"],
                user=cfg["user"],
                password=cfg["password"],
                connection_timeout=10,
                autocommit=True,
            )
    return _pool


def get_connection():
    """Return a pooled MySQL connection.  Falls back to a direct connection if
    the pool is exhausted or unavailable."""
    try:
        return _get_pool().get_connection()
    except RuntimeError:
        raise  # config/install error — propagate
    except Exception:
        # Pool exhausted — open a direct connection as safety valve
        if not MYSQL_AVAILABLE:
            raise RuntimeError("mysql-connector-python not installed.")
        cfg = _get_cfg()
        if not cfg["host"]:
            raise RuntimeError("MySQL host not configured.")
        return mysql.connector.connect(
            host=cfg["host"], port=cfg["port"],
            database=cfg["database"], user=cfg["user"], password=cfg["password"],
            connection_timeout=10, autocommit=True,
        )


# ── Password hashing ──────────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ── DB Initialisation ─────────────────────────────────────────────────────────
def init_db():
    """Create tables and seed default users. Safe to call multiple times."""
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            email        VARCHAR(128) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            username     VARCHAR(64) DEFAULT '',
            role         ENUM('admin','student','guest') DEFAULT 'student',
            theme_pref   ENUM('light','dark') DEFAULT 'light',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login   DATETIME,
            login_count  INT DEFAULT 0
        )
    """)

    # Login history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            username   VARCHAR(64) NOT NULL,
            logged_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            action     ENUM('login','logout','register') DEFAULT 'login'
        )
    """)

    # Seed default users if they don't exist
    defaults = [
        ("admin",   "dip2024",  "admin@dip.edu",   "admin"),
        ("student", "learn123", "student@dip.edu",  "student"),
        ("guest",   "guest",    "guest@dip.edu",    "guest"),
    ]
    for uname, pwd, email, role in defaults:
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (%s,%s,%s,%s)",
                (uname, _hash_password(pwd), email, role)
            )

    conn.commit()
    cur.close()
    conn.close()


# ── Authentication ────────────────────────────────────────────────────────────
def authenticate(email: str, password: str) -> dict | None:
    """
    Verify credentials using email. Returns user dict on success, None on failure.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, email, role, theme_pref, created_at FROM users "
        "WHERE email=%s AND password_hash=%s",
        (email.strip().lower(), _hash_password(password))
    )
    user = cur.fetchone()
    if user:
        cur.execute(
            "UPDATE users SET last_login=NOW(), login_count=login_count+1 WHERE id=%s",
            (user["id"],)
        )
        cur.execute(
            "INSERT INTO login_history (username, action) VALUES (%s,'login')",
            (user["username"] or user["email"],)
        )
        conn.commit()
    cur.close()
    conn.close()
    return user


# ── Registration ──────────────────────────────────────────────────────────────
def register_user(email: str, password: str, username: str = "", role: str = "student") -> tuple[bool, str]:
    """
    Create a new user using email. Returns (success: bool, message: str).
    """
    if "@" not in email or "." not in email:
        return False, "Invalid email address."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    email = email.strip().lower()
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close(); conn.close()
            return False, "Email already registered. Please sign in."
        cur.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (%s,%s,%s,%s)",
            (username, _hash_password(password), email, role)
        )
        cur.execute(
            "INSERT INTO login_history (username, action) VALUES (%s,'register')",
            (username or email,)
        )
        conn.commit()
        cur.close(); conn.close()
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Database error: {e}"


# ── Theme preference ──────────────────────────────────────────────────────────
def save_theme(username: str, theme: str):
    """Persist user's theme preference ('light' or 'dark')."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET theme_pref=%s WHERE username=%s", (theme, username))
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        pass  # Fail silently — theme is also in session_state


def get_theme(username: str) -> str:
    """Retrieve user's saved theme preference."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT theme_pref FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return row[0] if row else "light"
    except Exception:
        return "light"


# ── User info ─────────────────────────────────────────────────────────────────
def get_all_users() -> list[dict]:
    """Return list of all users (admin use)."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username, email, role, theme_pref, created_at, last_login, login_count "
            "FROM users ORDER BY created_at DESC"
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception:
        return []


def get_login_history(username: str = None, limit: int = 20) -> list[dict]:
    """Return recent login history."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        if username:
            cur.execute(
                "SELECT * FROM login_history WHERE username=%s ORDER BY logged_at DESC LIMIT %s",
                (username, limit)
            )
        else:
            cur.execute(
                "SELECT * FROM login_history ORDER BY logged_at DESC LIMIT %s", (limit,)
            )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Exception:
        return []


# ── Check DB connectivity ─────────────────────────────────────────────────────
def check_connection() -> tuple[bool, str]:
    """Test DB connection. Returns (ok: bool, message: str)."""
    try:
        conn = get_connection()
        conn.close()
        return True, "Connected to Railway MySQL ✅"
    except Exception as e:
        return False, f"DB Error: {e}"


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ok, msg = check_connection()
    print(msg)
    if ok:
        init_db()
        print("Database initialised with seed users.")
        u = authenticate("admin", "dip2024")
        print(f"Auth test: {u}")
