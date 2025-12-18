FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Also make sure we have uvicorn
RUN pip install --no-cache-dir uvicorn[standard]

# Copy application code
COPY . .

# Expose port
EXPOSE 8084

# Run the application
CMD ["uvicorn", "bridge:app", "--host", "0.0.0.0", "--port", "8084"]