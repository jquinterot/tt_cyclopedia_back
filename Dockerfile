FROM python:3.12-slim

# Install system dependencies for psycopg2 AND git
RUN apt-get update && \
    apt-get install -y libpq-dev gcc git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_app.py"]