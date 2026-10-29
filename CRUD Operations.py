```python
import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="BlogSpace | CRUD Operations",
    page_icon="📝",
    layout="wide"
)

DB_PATH = Path(__file__).parent / "blogspace.db"


# ---------------- DATABASE ----------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                author TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Support an existing Module 03 database.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(blogs)").fetchall()
        }

        if "category" not in columns:
            conn.execute(
                "ALTER TABLE blogs ADD COLUMN category TEXT NOT NULL DEFAULT 'General'"
            )

        if "author" not in columns:
            conn.execute(
                "ALTER TABLE blogs ADD COLUMN author TEXT NOT NULL DEFAULT 'Guest'"
            )

        if "updated_at" not in columns:
            conn.execute(
                "ALTER TABLE blogs ADD COLUMN updated_at TEXT"
            )
            conn.execute(
                "UPDATE blogs SET updated_at = created_at WHERE updated_at IS NULL"
            )


def create_blog(title, content, category, author):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO blogs
            (title, content, category, author, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, content, category, author, now, now))


def get_blogs(search="", category="All"):
    query = """
        SELECT * FROM blogs
        WHERE (title LIKE ? OR content LIKE ?)
    """
    pattern = f"%{search}%"
    params = [pattern, pattern]

    if category != "All":
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_blog(blog_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM blogs WHERE id = ?",
            (blog_id,)
        ).fetchone()


def update_blog(blog_id, title, content, category):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute("""
            UPDATE blogs
            SET title = ?, content = ?, category = ?, updated_at = ?
            WHERE id = ?
        """, (title, content, category, now, blog_id))


def delete_blog(blog_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM blogs WHERE id = ?",
            (blog_id,)
        )


initialize_database()


# ---------------- SESSION STATE ----------------

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "view_id" not in st.session_state:
    st.session_state.view_id = None


# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: #f7f8fc;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}

.hero {
    background: linear-gradient(120deg, #172554, #4f46e5);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📝 BlogSpace</h1>
    <