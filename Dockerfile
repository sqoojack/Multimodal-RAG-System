# Dockerfile

# Use Python 3.11 slim image
FROM python:3.11-slim

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure real-time logging output
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    ffmpeg \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and other necessary files
# Copy the src directory into /app/src
COPY src/ ./src/

# Expose Streamlit port
EXPOSE 8502

# Run Streamlit application pointing to the new path
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.port", "8502"]