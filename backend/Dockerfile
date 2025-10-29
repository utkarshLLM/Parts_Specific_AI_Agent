FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application files
COPY main.py .
COPY chat_handler.py .
COPY deepseek_client.py .
COPY product_service.py .
COPY vector_store.py .
COPY sample_products.py .
COPY scrapers.py .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with Gunicorn (production server)
CMD ["gunicorn", "--workers=4", "--threads=2", "--worker-class=gthread", "--bind=0.0.0.0:5000", "--timeout=120", "main:app"]