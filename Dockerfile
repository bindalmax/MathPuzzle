FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Prioritize IPv4 over IPv6 for dual-stack hosts (prevents AAAA connect timeouts on Ubuntu)
RUN echo "precedence ::ffff:0:0/96 100" >> /etc/gai.conf

# Copy application files
COPY . .

# Expose the application port
EXPOSE 5000

# Using standard threading for SocketIO (compatible with Python 3.13)
# Note: In production without eventlet/gevent, SocketIO might fallback to long-polling
CMD ["gunicorn", "--bind", "[::]:5000", "--workers", "1", "--threads", "100", "app:app"]
