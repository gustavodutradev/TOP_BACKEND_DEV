# # Exemplo de Dockerfile
# FROM python:3.10

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["python", "app.py"]

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production WSGI server
RUN pip install gunicorn

# Copy project files
COPY . .

# Create a non-root user for security
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Use Gunicorn as the production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:application"]