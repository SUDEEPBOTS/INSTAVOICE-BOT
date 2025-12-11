# ... after WORKDIR /app

# 1. Install system dependencies (ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. CRITICAL: Install setuptools via pip to resolve distutils dependency
RUN pip install --upgrade pip setuptools

# 3. Now install your Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ... rest of Dockerfile
