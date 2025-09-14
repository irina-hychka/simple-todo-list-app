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
from urllib.parse import quote_plus

# Read environment variables (with sensible defaults)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Encode password safely in case it contains special characters
DB_PASSWORD_Q = quote_plus(DB_PASSWORD)

# Build PostgreSQL URI if host is defined, otherwise fallback to SQLite
if DB_HOST and DB_NAME and DB_USER:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_Q}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
else:
    # Fallback for local development: SQLite file in project directory
    SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"
