# Base image
FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# 👇 Remove the strict offline install for build-time install
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY . .

# Default command
CMD ["python", "main_hackathon_optimized.py"]
