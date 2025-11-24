FROM python:3.10-slim

# Install system dependencies for psycopg2 and build tools
RUN apt-get update && \
    apt-get install -y gcc libpq-dev build-essential git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files (including app/, start_worker.sh, etc.)
COPY . .

# Make the script executable
RUN chmod +x /code/start_worker.sh

# Avoid Python buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Default command: run FastAPI app
CMD ["/code/start_worker.sh"]
