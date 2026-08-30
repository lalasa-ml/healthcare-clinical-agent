# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing bytecode and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first
COPY requirements.txt .

# Upgrade pip and install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose API and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Default command (will be overridden per service or used as baseline)
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]