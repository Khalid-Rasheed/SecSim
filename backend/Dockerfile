# SecSim backend — Flask API (production image).
# Served with gunicorn (multi-worker); NEVER use run.py's debug server here.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first (cached unless requirements change).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# run:app is the factory-built Flask instance from run.py.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]
