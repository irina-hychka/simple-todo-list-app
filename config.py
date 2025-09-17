"""
config.py — Database configuration helper for the To-Do List app.

This module builds the SQLAlchemy connection string (URI) based on environment variables.
It supports two modes:
- PostgreSQL (preferred, e.g., AWS RDS)
- SQLite fallback for local development

Environment Variables:
    DB_HOST     (e.g. "todo-rds.abcdef123.us-east-1.rds.amazonaws.com")
    DB_PORT     (default: 5432)
    DB_NAME     (e.g. "todo_db")
    DB_USER     (e.g. "todo_admin")
    DB_PASSWORD (e.g. "secret")
"""

import os
import json
from urllib.parse import quote_plus

def _maybe_from_json(val: str, key: str) -> str:
    """
    If val looks like JSON -> return obj[key] if present, else original val.
    """
    if not val:
        return val
    val = val.strip()
    if val.startswith("{") and val.endswith("}"):
        try:
            obj = json.loads(val)
            if isinstance(obj, dict) and key in obj and obj[key] is not None:
                return str(obj[key])
        except Exception:
            pass
    return val

# Raw envs
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# If secrets came as JSON (RDS credentials), extract needed fields
# e.g. {"username":"todo_admin","password":"..."}
DB_USER = _maybe_from_json(DB_USER, "username") or DB_USER
DB_PASSWORD = _maybe_from_json(DB_PASSWORD, "password") or DB_PASSWORD

# Quote password for special characters
DB_PASSWORD_Q = quote_plus(DB_PASSWORD) if DB_PASSWORD is not None else ""

# Build URI (Postgres preferred) or fallback to SQLite locally
if DB_HOST and DB_NAME and (DB_USER is not None):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_Q}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"
