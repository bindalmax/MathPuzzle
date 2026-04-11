# MathPuzzle VPS & Docker Deployment Plan

## Executive Summary

The MathPuzzle application is **production-ready** for EU VPS deployment. It has:
- ✅ Docker containerization (Python 3.11 + Gunicorn)
- ✅ PostgreSQL database integration (SQLAlchemy ORM)
- ✅ Environment-based configuration
- ✅ Production compose file (`docker-compose.prod.yml`)
- ✅ Full WebSocket support for multiplayer

---

## Part 1: VPS Compatibility Assessment

### Current Stack Compatibility: ✅ FULLY COMPATIBLE

| Component | Status | Details |
|-----------|--------|---------|
| Python 3.11 | ✅ | Slim base image for minimal footprint |
| Flask Framework | ✅ | Lightweight, production-ready |
| Gunicorn WSGI | ✅ | Configured in Dockerfile (workers + threading) |
| Flask-SocketIO | ✅ | WebSocket support with threading async mode |
| PostgreSQL | ✅ | Docker Postgres 15-Alpine with persistent volumes |
| SQLAlchemy ORM | ✅ | Flask-SQLAlchemy + database models ready |
| SSL/TLS Support | ✅ | Environment-based cert configuration |
| Static Files | ✅ | Served via reverse proxy (Nginx) |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Nginx (Reverse Proxy)                      │
│  - SSL/TLS Termination                                  │
│  - Static file serving                                  │
│  - Load balancing (optional)                            │
│  - WebSocket upgrade handling                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Docker Container - Web Application              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Gunicorn WSGI Server (workers + threading)     │   │
│  │  - 1 worker, 100 threads                         │   │
│  │  - Handles HTTP requests & WebSockets           │   │
│  └────────────┬─────────────────────────────────────┘   │
│               │                                         │
│  ┌────────────▼─────────────────────────────────────┐   │
│  │       Flask Application                          │   │
│  │  - Game logic, API routes                        │   │
│  │  - SocketIO event handlers                       │   │
│  │  - Session management                           │   │
│  └────────────┬─────────────────────────────────────┘   │
└─────────────────┼─────────────────────────────────────────┘
                  │ TCP Connection
                  ▼
┌─────────────────────────────────────────────────────────┐
│    Docker Container - PostgreSQL Database               │
│  - Postgres 15-Alpine                                   │
│  - Persistent volume mount                              │
│  - Healthcheck enabled                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Part 2: Recommended EU VPS Providers

### Top Recommendations (Price + GDPR Compliance)

| Provider | Starting Price | Best For | Data Centers | GDPR | Notes |
|----------|---|---|---|---|---|
| **Hetzner** 🏆 | €3.99/mo | **BEST VALUE** | Germany, Finland | ✅ | DPA available, excellent support |
| **OVHcloud** | €3.50/mo | Budget + EU compliance | France, Poland, Germany | ✅ | GDPR-certified, mature platform |
| **Linode (EU)** | €5/mo | Reliability | UK, Germany, France | ✅ | Well-documented, great API |
| **Vultr (EU)** | €2.50/mo | Performance | Netherlands, France, UK | ✅ | SSD-backed, DDoS included |
| **DigitalOcean** | €4.70/mo | Developer-friendly | Amsterdam, Frankfurt | ✅ | Excellent docs, app marketplace |
| **Scaleway** | €6.99/mo | Compute-heavy | France, Netherlands | ✅ | Modern infrastructure |

### Recommended Specs

- **CPU**: 2 cores minimum (Docker + App + DB)
- **RAM**: 4GB minimum (2GB for DB, 2GB for App)
- **Storage**: 50GB SSD minimum
- **Bandwidth**: 1TB/month sufficient
- **Price Range**: €3-10/month (all recommendations fit)

---

## Part 3: Current Setup Verification

### Existing Docker Configuration

**Dockerfile**
- Base: `python:3.11-slim`
- Gunicorn with threading (compatible with Python 3.13)
- 1 worker, 100 threads
- Port: 5000

**docker-compose.yml** (development)
- PostgreSQL 15-Alpine service
- Web service with volume mounts
- Environment-based configuration
- Health check on database

**docker-compose.prod.yml** (production)
- Simplified for cloud deployment
- No local SSL certs (proxy handles it)
- Gunicorn on port 5000
- Environment variables for DATABASE_URL

**Database Layer**
- SQLAlchemy ORM configured
- Highscore model with proper schema
- Flask-SQLAlchemy integration
- DATABASE_URL supports PostgreSQL

**Environment Configuration**
- SECRET_KEY (required in production)
- DATABASE_URL (PostgreSQL connection string)
- ALLOWED_ORIGINS (CORS security)
- FLASK_ENV (development/production toggle)

---

## Part 3.5: Domain Name Options

### Option A: Running WITHOUT a Domain (IP Address Only)

**Best for:** Testing, MVP, development, or temporary deployments.

#### Setup Steps:

1. **Deploy directly with IP address:**
```bash
# Replace your-vps-ip with actual IP (e.g., 123.45.67.89)
# Access application: http://123.45.67.89:5000

# No domain required - works immediately!
```

2. **Access via IP (without Nginx/SSL initially):**
```bash
# In docker-compose.prod.yml, expose port directly
# http://your-vps-ip:5000

# Update ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=123.45.67.89
```

3. **Simplified docker-compose (no SSL/Nginx):**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"  # Direct port exposure
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - ALLOWED_ORIGINS=123.45.67.89
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

4. **Deploy without domain:**
```bash
# SSH to VPS
ssh root@123.45.67.89

# Create app directory
mkdir -p /app/mathpuzzle && cd /app/mathpuzzle
git clone <repo-url> .

# Set environment
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_USER=mathuser
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=mathpuzzle
DATABASE_URL=postgresql://mathuser:$(cat .env | grep POSTGRES_PASSWORD | cut -d= -f2)@db:5432/mathpuzzle
ALLOWED_ORIGINS=123.45.67.89
FLASK_ENV=production
EOF

# Deploy
docker compose up -d

# Access: http://123.45.67.89:5000
```

#### Pros & Cons

| Aspect | Details |
|--------|---------|
| ✅ Pros | No domain cost, immediate deployment, simple setup |
| ❌ Cons | No SSL/HTTPS (insecure for production), IP address may change, unprofessional appearance |
| 🎯 Use Case | Development, testing, internal tools, MVP validation |

---

### Option B: Get a Domain Name (Professional Deployment)

**Best for:** Production deployments, professional applications, long-term hosting.

#### Step 1: Choose a Domain Registrar

| Registrar | TLD Options | Starting Price | GDPR | Notes |
|-----------|---|---|---|---|
| **Namecheap** 🏆 | 800+ | €0.88/yr | ✅ | Best value, WHOIS protection included |
| **OVHcloud** | 400+ | €1.50/yr | ✅ | EU-based, integrated hosting |
| **GoDaddy** | 500+ | €2.99/yr | ✅ | Popular, large marketplace |
| **Ionos** | 300+ | €0.99/yr | ✅ | Budget-friendly, EU-based |
| **Domain.com** | 600+ | €1.49/yr | ✅ | Simple interface |

#### Step 2: Domain Recommendations

Choose based on your use case:

| Domain Extension | Cost | Use Case | Example |
|---|---|---|---|
| **.com** | €8-12/yr | Professional, games | mathpuzzle.com |
| **.io** | €35-40/yr | Tech, startups | mathpuzzle.io |
| **.app** | €15-18/yr | Applications | mathpuzzle.app |
| **.game** | €25-30/yr | Gaming | mathpuzzle.game |
| **.eu** | €5-8/yr | EU-focused | mathpuzzle.eu |
| **.online** | €3-6/yr | Generic | mathpuzzle.online |
| **.co** | €12-15/yr | Modern alternative | mathpuzzle.co |

#### Step 3: Purchase Domain

**Example on Namecheap:**

1. Go to https://www.namecheap.com/
2. Search for your desired domain (e.g., "mathpuzzle.game")
3. Add to cart and checkout
4. Enable WHOIS protection (free on Namecheap)
5. Note your nameservers provided

#### Step 4: Point Domain to VPS IP

**Option B1: Update Nameservers (Recommended)**

```bash
# At registrar (Namecheap), update nameservers to:
# ns1.digitalocean.com (if using DigitalOcean)
# ns1.linode.com (if using Linode)
# Or use your VPS provider's nameservers

# Wait 24-48 hours for DNS propagation
# Verify with:
nslookup mathpuzzle.game
dig mathpuzzle.game
```

**Option B2: DNS A Record (Direct)**

1. Go to your registrar's DNS settings
2. Add an **A Record**:
   - **Name**: @ (or empty)
   - **Type**: A
   - **Value**: Your VPS IP (e.g., 123.45.67.89)
   - **TTL**: 3600 (1 hour)
3. Add **www subdomain**:
   - **Name**: www
   - **Type**: A
   - **Value**: Your VPS IP
   - **TTL**: 3600

Example DNS Records:
```
@ (root)        A       123.45.67.89        3600
www             A       123.45.67.89        3600
mail            MX      10 mail.example.com 3600
```

#### Step 5: Verify DNS Propagation

```bash
# Wait 5 minutes to 48 hours

# Check DNS resolution
nslookup mathpuzzle.game
dig mathpuzzle.game +short

# Test ping
ping mathpuzzle.game

# Expected output:
# PING mathpuzzle.game (123.45.67.89): 56 data bytes
```

#### Step 6: Update VPS Configuration

Once domain is active, update your deployment:

```bash
# SSH to VPS
ssh root@your-vps-ip

# Update .env
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_USER=mathuser
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=mathpuzzle
DATABASE_URL=postgresql://mathuser:$(cat .env | grep POSTGRES_PASSWORD | cut -d= -f2)@db:5432/mathpuzzle
ALLOWED_ORIGINS=mathpuzzle.game,www.mathpuzzle.game
FLASK_ENV=production
EOF

# Restart services
docker compose down
docker compose -f docker-compose.prod.yml up -d
```

#### Step 7: Enable SSL with Let's Encrypt

Once domain points to your VPS:

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate (standalone mode)
certbot certonly --standalone \
  -d mathpuzzle.game \
  -d www.mathpuzzle.game \
  -d mail.mathpuzzle.game

# Auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

# Verify
certbot certificates
```

#### Pros & Cons

| Aspect | Details |
|--------|---------|
| ✅ Pros | Professional appearance, SSL/HTTPS available, personal branding, easier to share |
| ❌ Cons | Annual cost (€1-40), domain registration overhead, DNS propagation delay |
| 🎯 Use Case | Production, professional apps, long-term projects |

---

### Option C: Hybrid Approach (Recommended for MVP)

**Best for:** Launching quickly while planning for production.

#### Phase 1: Quick Launch (Week 1-2)
- Deploy on IP address: `http://123.45.67.89:5000`
- Test functionality, gather user feedback
- No SSL needed initially
- Share IP with small user group

#### Phase 2: Add Domain (Week 3+)
- Purchase domain (€2-30 for first year)
- Point to VPS IP
- Update ALLOWED_ORIGINS
- Enable SSL with Let's Encrypt
- Share professional URL: `https://mathpuzzle.game`

#### Phase 3: Production (Week 4+)
- Add Nginx reverse proxy
- Configure SSL renewal automation
- Set up monitoring and backups
- Scale if needed

---

## Part 4: Deployment Steps

### Step 1: VPS Initial Setup

```bash
# SSH into VPS as root
ssh root@your-vps-ip

# Update system packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose plugin
apt install -y docker-compose-plugin

# Create app directory
mkdir -p /app/mathpuzzle
cd /app/mathpuzzle

# Clone repository
git clone <your-repository-url> .
```

### Step 2: Environment Configuration

```bash
# Create .env file with secure values
cat > .env << 'EOF'
# Generate secure SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Generate secure database password
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_USER=mathuser
POSTGRES_DB=mathpuzzle

# Build DATABASE_URL
DATABASE_URL=postgresql://mathuser:${POSTGRES_PASSWORD}@db:5432/mathpuzzle

# Set allowed origins for CORS
ALLOWED_ORIGINS=your-domain.com,www.your-domain.com

# Flask environment
FLASK_ENV=production
EOF

# Verify .env created
cat .env
```

### Step 3: Deploy with Docker Compose

```bash
# Navigate to app directory
cd /app/mathpuzzle

# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Start services (detached mode)
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose logs -f web

# Wait for database to be ready (healthcheck)
docker compose exec db pg_isready -U mathuser -d mathpuzzle
```

### Step 4: Initialize Database

```bash
# Access Flask shell to create tables
docker compose exec web python -c "from database import db; from app import app; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
```

### Step 5: Add Nginx Reverse Proxy (Recommended)

Create `/app/mathpuzzle/nginx.conf`:

```nginx
upstream web {
    server web:5000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://web;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://web/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Update `docker-compose.prod.yml` to include Nginx:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web

  web:
    build: .
    # ... rest of configuration

  db:
    image: postgres:15-alpine
    # ... rest of configuration
```

### Step 6: SSL Certificate with Let's Encrypt

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Create certificate (standalone mode initially)
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Enable auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

# Verify renewal works
certbot renew --dry-run
```

### Step 7: Verify Deployment

```bash
# Check container status
docker compose ps

# Check web service logs
docker compose logs web

# Test database connection
docker compose exec db psql -U mathuser -d mathpuzzle -c "SELECT version();"

# Test application endpoint
curl http://localhost:5000/
# or with HTTPS
curl https://your-domain.com/
```

---

## Part 5: Post-Deployment Tasks

### Monitoring & Maintenance

```bash
# View real-time logs
docker compose logs -f

# Check resource usage
docker stats

# Backup database
docker compose exec db pg_dump -U mathuser mathpuzzle > backup_$(date +%Y%m%d).sql

# Restore database
docker compose exec -T db psql -U mathuser mathpuzzle < backup_20260410.sql

# Restart services
docker compose restart

# Update images
docker compose pull && docker compose up -d
```

### Persistent Backups

```bash
# Create backup script: /app/mathpuzzle/backup.sh
#!/bin/bash
BACKUP_DIR="/app/mathpuzzle/backups"
mkdir -p $BACKUP_DIR
docker compose exec -T db pg_dump -U mathuser mathpuzzle | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Schedule daily backup (crontab -e)
0 2 * * * cd /app/mathpuzzle && bash backup.sh
```

### Auto-Restart & Health Monitoring

```bash
# Docker already has restart policy: always
# For additional monitoring, use Watchtower to auto-update images

docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 86400
```

---

## Part 6: Pre-Deployment Checklist

### Security
- [ ] Generate strong `SECRET_KEY` (32+ hex chars)
- [ ] Generate strong PostgreSQL password (16+ hex chars)
- [ ] Set `ALLOWED_ORIGINS` to exact domain(s)
- [ ] Enable SSL/TLS certificate (Let's Encrypt)
- [ ] Configure Nginx security headers
- [ ] Review environment variables for no hardcoded secrets
- [ ] Enable Docker restart policies

### Configuration
- [ ] Update domain name in nginx.conf
- [ ] Verify DATABASE_URL format is correct
- [ ] Test locally with `docker compose up` first
- [ ] Verify .env file is in .gitignore
- [ ] Create backup strategy and scripts
- [ ] Set up log rotation for Docker containers

### Testing
- [ ] Test web app access (http → https redirect)
- [ ] Test WebSocket connection (multiplayer game)
- [ ] Test database connectivity (health check passes)
- [ ] Test highscore save/retrieve
- [ ] Test leaderboard functionality
- [ ] Verify SSL certificate is valid
- [ ] Test with different browsers/devices

### Post-Deployment
- [ ] Monitor logs for errors: `docker compose logs -f`
- [ ] Set up automated backups
- [ ] Set up monitoring/alerting
- [ ] Document access procedures for team
- [ ] Create runbook for common maintenance tasks
- [ ] Plan for scaling (if needed)

---

## Part 7: Troubleshooting Guide

### Database Connection Issues

```bash
# Check if database is running and healthy
docker compose ps db

# Test connection
docker compose exec db psql -U mathuser -d mathpuzzle -c "SELECT 1;"

# View database logs
docker compose logs db

# Reset database (WARNING: destructive)
docker compose down -v
docker compose up -d
```

### WebSocket Connection Issues

```bash
# Check if SocketIO namespace is accessible
curl -i http://localhost:5000/socket.io/?EIO=4&transport=polling

# View web app logs for SocketIO errors
docker compose logs web | grep -i socket

# Verify proxy configuration in nginx.conf (Connection: Upgrade headers)
```

### SSL Certificate Issues

```bash
# Check certificate expiry
certbot certificates

# Verify SSL configuration
ssl_test_url="https://your-domain.com"
openssl s_client -connect your-domain.com:443 -tls1_2

# Check Nginx SSL configuration
docker compose exec nginx nginx -t
```

### Performance Issues

```bash
# Monitor Docker resource usage
docker stats

# Scale Gunicorn workers (edit Dockerfile or docker-compose.prod.yml)
# Increase: --workers 4 --threads 100

# Check database slow queries
docker compose exec db psql -U mathuser -d mathpuzzle \
  -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

---

## Part 8: Scaling Considerations

### For Single VPS (Current Setup)
- ✅ Suitable for: 100-1000 concurrent users
- ✅ Gunicorn: 1 worker, 100 threads
- ✅ PostgreSQL: Single instance
- ✅ Storage: PostgreSQL persistent volume

### For Multi-Server Deployment (Future)
- Add load balancer (Nginx, HAProxy)
- Scale Gunicorn workers to 4+
- Migrate database to managed PostgreSQL (AWS RDS, Azure DB, etc.)
- Add Redis for session management
- Implement shared file storage (S3, MinIO) for assets

---

## Part 9: Quick Reference Commands

### Common Operations

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f web

# View database logs
docker compose logs -f db

# Execute commands in containers
docker compose exec web bash
docker compose exec db psql -U mathuser -d mathpuzzle

# Rebuild application
docker compose -f docker-compose.prod.yml build --no-cache

# Check service health
docker compose ps
```

### Database Operations

```bash
# Connect to database
docker compose exec db psql -U mathuser -d mathpuzzle

# Backup database
docker compose exec db pg_dump -U mathuser mathpuzzle > backup.sql

# Restore database
docker compose exec -T db psql -U mathuser mathpuzzle < backup.sql

# Check database size
docker compose exec db psql -U mathuser -d mathpuzzle -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

---

## References & Resources

- **Docker Official Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Gunicorn Documentation**: https://gunicorn.org/
- **Flask-SocketIO**: https://flask-socketio.readthedocs.io/

---

**Plan Created**: 2026-04-10  
**Status**: Ready for Implementation  
**Next Steps**: Execute deployment steps in order, starting with VPS provider selection and environment setup.
