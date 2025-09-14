# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Disable pip cache and reduce layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Flask listens 5000
EXPOSE 5000

# Healthcheck Docker-level
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
