FROM python:3.10-slim

# Install system dependencies for psycopg2 and build tools
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files (including app/ and wx_data if needed)
COPY . .

# Avoid Python buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY start_worker.sh /usr/src/app/start_worker.sh
WORKDIR /usr/src/app