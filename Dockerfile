# ✅ Fixed Python version (important for TensorFlow)
FROM python:3.10.13-slim

# Prevent Python issues
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (for OpenCV + DeepFace)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for faster rebuilds)
COPY requirements.txt .

# Upgrade pip tools + install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

# Expose port (Render uses dynamic PORT env)
EXPOSE 10000

# Start app (Render-compatible)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 run:app"]