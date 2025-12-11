FROM python:3.9-slim

WORKDIR /app

# 1. Install system dependencies FIRST
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of the application
COPY . .

# 4. Create necessary directories
RUN mkdir -p sessions temp logs temp_voices

# 5. Set the command to run your bot
CMD ["python", "main.py"]
