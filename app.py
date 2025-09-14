"""
app.py — Simple To-Do List Application (Flask + SQLAlchemy)

Features:
- REST API for tasks (CRUD)
- Status filtering (all | active | completed)
- Bulk delete by status
- Health endpoint for liveness and DB checks
- SQLite fallback for local/dev environments if DB is not configured

Environment Variables:
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD (for PostgreSQL)
- PORT (optional; defaults to 5000)

Usage:
    # Local SQLite (no env variables)
    python app.py

    # With PostgreSQL (RDS)
    export DB_HOST=...
    export DB_USER=...
    export DB_PASSWORD=...
    python app.py
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

# Optional: auto-load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import connection string builder (env-based with SQLite fallback)
from config import SQLALCHEMY_DATABASE_URI  # noqa: E402

# Allow DATABASE_URL override (useful for Heroku-style environments)
DATABASE_URI = os.getenv("DATABASE_URL", SQLALCHEMY_DATABASE_URI)

# -----------------------------------------------------------------------------
# Database setup
# -----------------------------------------------------------------------------
Base = declarative_base()
engine = create_engine(
    DATABASE_URI,
    future=True,
    pool_pre_ping=True,   # validates connections before using
    pool_recycle=300,     # refreshes connections periodically
)

# Thread-local scoped session registry
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False)
)

# -----------------------------------------------------------------------------
# Flask app initialization
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI


class Task(Base):
    """
    ORM entity for a to-do item.

    Columns:
    - id (int, PK): unique identifier
    - title (str, ≤ 255 chars): task title (required)
    - is_done (bool): completion flag (default: False)
    - created_at (datetime): UTC creation timestamp
    """

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Auto-create schema if it doesn't exist (safe for dev/local use)
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    Get tasks with optional status filtering.

    Query params:
        status: "all" (default), "active", or "completed"

    Returns:
        200 OK, JSON list of tasks:
        [
            {"id": 1, "title": "...", "is_done": false, "created_at": "ISO8601"},
            ...
        ]
    """
    status = request.args.get("status", "all")
    db = SessionLocal()
    try:
        q = db.query(Task)
        if status == "active":
            q = q.filter(Task.is_done.is_(False))
        elif status == "completed":
            q = q.filter(Task.is_done.is_(True))
        tasks = q.order_by(Task.created_at.desc()).all()
        return jsonify([
            {
                "id": t.id,
                "title": t.title,
                "is_done": t.is_done,
                "created_at": t.created_at.isoformat(),
            } for t in tasks
        ])
    finally:
        db.close()


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """
    Create a new task.

    Request JSON:
        {"title": "Buy milk"}

    Validations:
        - title is required, trimmed, non-empty

    Returns:
        200 OK, created task JSON
        400 Bad Request if validation fails
    """
    data = request.json or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    db = SessionLocal()
    try:
        task = Task(title=title)
        db.add(task)
        db.commit()
        db.refresh(task)
        return jsonify({
            "id": task.id,
            "title": task.title,
            "is_done": task.is_done,
            "created_at": task.created_at.isoformat(),
        })
    finally:
        db.close()


@app.route("/api/tasks/<int:task_id>/toggle", methods=["PATCH"])
def toggle_task(task_id):
    """
    Toggle completion status for a specific task.

    Path params:
        task_id (int)

    Returns:
        200 OK with updated task JSON
        404 Not Found if task does not exist
    """
    db = SessionLocal()
    try:
        task = db.get(Task, task_id)
        if not task:
            return jsonify({"error": "not found"}), 404
        task.is_done = not task.is_done
        db.commit()
        db.refresh(task)
        return jsonify({
            "id": task.id,
            "title": task.title,
            "is_done": task.is_done,
            "created_at": task.created_at.isoformat(),
        })
    finally:
        db.close()


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Delete a task by ID.

    Path params:
        task_id (int)

    Returns:
        204 No Content on success
        404 Not Found if task does not exist
    """
    db = SessionLocal()
    try:
        task = db.get(Task, task_id)
        if not task:
            return jsonify({"error": "not found"}), 404
        db.delete(task)
        db.commit()
        return ("", 204)
    finally:
        db.close()


@app.route("/api/tasks", methods=["DELETE"])
def bulk_delete():
    """
    Bulk delete tasks by status.

    Query params:
        status: "all" (default), "active", or "completed"

    Returns:
        200 OK, {"deleted": <int>}
    """
    status = request.args.get("status", "all")
    db = SessionLocal()
    try:
        q = db.query(Task)
        if status == "active":
            q = q.filter(Task.is_done.is_(False))
        elif status == "completed":
            q = q.filter(Task.is_done.is_(True))
        deleted = q.delete(synchronize_session=False)
        db.commit()
        return jsonify({"deleted": deleted})
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Health check & UI
# -----------------------------------------------------------------------------
@app.route("/health")
def health():
    """
    Liveness/DB readiness probe.

    Returns:
        200 OK {"status": "ok"} if DB connection works
        500 {"status": "db_error"} if DB query fails
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}, 200
    except SQLAlchemyError as e:
        return {"status": "db_error", "detail": e.__class__.__name__}, 500


@app.route("/")
def index():
    """
    Serve the main UI template.
    The UI consumes JSON API endpoints defined above.
    """
    return render_template("index.html")

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
