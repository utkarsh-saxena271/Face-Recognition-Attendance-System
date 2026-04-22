FROM python:3.10-slim

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Render uses dynamic port
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 run:app"]
