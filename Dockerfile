FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create working directory
WORKDIR /app

# Create data directory for the local SQLite database
RUN mkdir -p /app/data

# Install python dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source code
COPY . .

# Expose the port FastAPI listens on
EXPOSE 8000

# Default start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
