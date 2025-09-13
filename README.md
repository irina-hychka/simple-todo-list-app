# Simple To-Do List App

A minimal yet modern **to-do list web application** built with **Flask, SQLAlchemy, and Vanilla JavaScript**.

It runs locally with **SQLite** and can easily be migrated to **PostgreSQL on AWS RDS** for cloud deployment (Elastic Beanstalk / ECS / EKS).

## ✨ Features
- Add, toggle, and delete tasks
- Bulk actions: *Clear All* / *Clear Completed*
- Task filtering: *All / Active / Completed*
- Responsive dark theme UI
- Toast notifications for user feedback
- Health endpoint (`/health`) for monitoring and load balancers

## 🚀 Getting Started

### Requirements
- Python 3.9+
- pip

### Local setup
```bash
cd simple-todo-list-app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py

### Screenshot
![App screenshot](./screenshots/app-screenshot.png)