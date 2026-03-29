FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the application port
EXPOSE 5000

# Using standard threading for SocketIO (compatible with Python 3.13)
# Note: In production without eventlet/gevent, SocketIO might fallback to long-polling
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "100", "app:app"]
