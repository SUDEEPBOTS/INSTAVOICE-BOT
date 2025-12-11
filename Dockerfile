# 1. Define the base image
FROM python:3.9-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install system dependencies (ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 4. Upgrade pip and install setuptools BEFORE requirements
RUN pip install --upgrade pip setuptools

# 5. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Create necessary directories
RUN mkdir -p sessions temp logs temp_voices

# 8. Set the command to run your bot
CMD ["python", "main.py"]
