FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

COPY . .

RUN chmod -R 755 /app

RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "--threads", "2", "--timeout", "120", "--worker-class", "gthread", "--worker-tmp-dir", "/dev/shm", "app:application"]