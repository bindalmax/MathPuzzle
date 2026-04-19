# Cloud Deployment Plan - MathPuzzle

**Last Updated**: April 19, 2026  
**Project Status**: PRODUCTION-READY ✓  
**Recommended AWS Architecture**: ECS Fargate + RDS PostgreSQL + ALB + CloudFront

---

## 🚀 AWS DEPLOYMENT QUICK START (Deploy Today)

### Current Project State (April 2026)
✓ Database migration **COMPLETE** (PostgreSQL ORM)  
✓ Docker containerization **READY** (docker-compose.prod.yml)  
✓ Environment configuration **COMPREHENSIVE** (all cloud-ready)  
✓ Security hardening **COMPLETE** (CSRF, rate limiting, OAuth2)  
✓ WebSocket multiplayer **IMPLEMENTED** (production-tested)  
✓ No local SSL needed in production ✓  

### Fastest AWS Deployment: AWS Elastic Beanstalk (1-2 hours)

**Why EB for quick deployment:**
- Auto-handles Docker deployment from Dockerfile
- Managed RDS PostgreSQL integration
- Automatic scaling & load balancing
- Instant HTTPS with AWS Certificate Manager
- Zero infrastructure management

**Steps to deploy NOW:**

1. **Generate deployment credentials**:
   ```bash
   # Generate strong SECRET_KEY
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Create `.ebextensions/env.config`** in repo root:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       FLASK_ENV: production
       SECRET_KEY: <your-generated-secret-key>
       DATABASE_URL: <RDS-connection-string>
       ALLOWED_ORIGINS: https://yourdomain.com
   ```

3. **Deploy with AWS CLI**:
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize (one-time)
   eb init -p "Docker running on 64bit Amazon Linux 2" mathpuzzle
   
   # Create environment with PostgreSQL
   eb create mathpuzzle-prod --instance-type t3.medium --database --database.engine postgres
   
   # Deploy
   eb deploy
   ```

4. **Verify deployment**:
   ```bash
   eb open  # Opens the app in browser
   eb logs  # Check logs
   ```

---

## ☁️ COMPREHENSIVE AWS DEPLOYMENT OPTIONS

### Option 1: AWS Elastic Beanstalk (RECOMMENDED FOR QUICK DEPLOYMENT)
**Time to Production**: 1-2 hours  
**Best For**: Quick deployment, minimal DevOps knowledge needed

**Architecture**:
- EB manages Docker container deployment
- RDS PostgreSQL (managed database)
- ALB (Application Load Balancer) with auto-scaling
- AWS Certificate Manager (free HTTPS)
- CloudWatch (logging & monitoring)

**Pros**:
- ✅ Fastest deployment option
- ✅ Auto-scaling included
- ✅ One-command deployment (`eb deploy`)
- ✅ Free HTTPS
- ✅ Minimal AWS knowledge required

**Cons**:
- Less granular control than ECS
- EC2 instances (not serverless)

**Setup Checklist**:
- [ ] AWS Account with appropriate IAM permissions
- [ ] AWS CLI v2 installed
- [ ] EB CLI installed (`pip install awsebcli`)
- [ ] `.ebextensions/` folder created with configuration
- [ ] GitHub repository (optional, for CI/CD)

**Cost Estimate**: ~$20-50/month (includes t3.medium EC2 + RDS)

---

### Option 2: AWS ECS Fargate (RECOMMENDED FOR PRODUCTION)
**Time to Production**: 2-4 hours  
**Best For**: Scalable, production-grade deployments

**Architecture**:
```
GitHub → ECR (Docker Registry) → ECS Fargate (Containers)
         ↓
    CloudFront (CDN)
         ↓
    ALB (Load Balancer)
         ↓
    ECS Fargate Tasks
         ↓
    RDS PostgreSQL
         ↓
    CloudWatch Logs
```

**Setup Steps**:

1. **Push Docker image to ECR**:
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name mathpuzzle
   
   # Get login credentials
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   docker build -t mathpuzzle:latest .
   docker tag mathpuzzle:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mathpuzzle:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mathpuzzle:latest
   ```

2. **Create RDS PostgreSQL Database**:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier mathpuzzle-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username mathuser \
     --master-user-password <strong-password> \
     --allocated-storage 20 \
     --publicly-accessible false
   ```

3. **Create ECS Cluster, Task Definition & Service** (via AWS Console or Terraform)

4. **Configure ALB** with target group pointing to ECS service

5. **Set up CloudFront** for static assets

**Pros**:
- ✅ Fully managed containers (no EC2 maintenance)
- ✅ Auto-scaling based on CPU/memory
- ✅ High availability across AZs
- ✅ Better cost efficiency than EC2
- ✅ Production-grade

**Cons**:
- More complex setup
- Requires Docker registry (ECR)

**Cost Estimate**: ~$30-80/month (Fargate + RDS)

---

### Option 3: AWS Lambda + API Gateway (SERVERLESS)
**Time to Production**: 3-5 hours  
**Best For**: Low-traffic applications, cost-conscious

**⚠️ Limitations**: 
- Lambda timeout: 15 minutes (not suitable for long WebSocket connections)
- Not recommended for real-time multiplayer (WebSockets limited)
- Cold start issues

**Note**: Not recommended for this project due to WebSocket multiplayer feature.

---

## 📋 PRE-DEPLOYMENT CHECKLIST (All Steps COMPLETE ✓)

- [x] **Cloud-Aware SSL**: Already implemented in `app.py` (no local SSL in production)
- [x] **Health Checks**: Routes return 200 OK for load balancer pings
- [x] **Dependencies**: `requirements.txt` has all cloud-ready packages (psycopg2, gunicorn)
- [x] **Database**: SQLAlchemy ORM supports PostgreSQL
- [x] **Docker**: `Dockerfile` and `docker-compose.prod.yml` ready
- [x] **Environment Configuration**: All env vars properly handled
- [x] **Security**: CSRF protection, rate limiting, secret key enforcement
- [x] **Multiplayer/WebSocket**: Production-ready threading mode

---

## 🔧 DEPLOYMENT CONFIGURATION FOR AWS

### Required Environment Variables

```bash
# Set these in AWS console, EB, ECS, or Parameter Store
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/mathpuzzle
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
PORT=5000
```

### Application Configuration Files

**Already in place**:
- ✓ `Dockerfile` (Python 3.11-slim, Gunicorn)
- ✓ `docker-compose.prod.yml` (cloud-optimized, no local SSL)
- ✓ `requirements.txt` (all dependencies listed)

### Database Connection Pooling (Production Recommendation)

Add to `app.py` or database configuration for better performance:
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

---

## 🧪 TESTING BEFORE DEPLOYMENT

### Phase 1: Local Docker Test
```bash
# Test Docker build and run
docker build -t mathpuzzle:latest .
docker run -e FLASK_ENV=production -p 5000:5000 mathpuzzle:latest
# Visit http://localhost:5000 and verify
```

### Phase 2: Docker Compose with Postgres Test
```bash
# Test with actual PostgreSQL
docker-compose -f docker-compose.prod.yml up -d
# Verify at http://localhost:8080
docker-compose logs -f web
```

### Phase 3: Run Full Test Suite
```bash
python run_tests.py
# All tests should pass
```

### Phase 4: AWS-Specific Tests
- [ ] Test with RDS PostgreSQL (use test environment first)
- [ ] Verify WebSocket connections through ALB
- [ ] Test multiplayer with 2+ simultaneous users
- [ ] Verify database persistence after redeployment
- [ ] Check CloudWatch logs for errors

---

## 📊 DEPLOYMENT COMPARISON TABLE

| Aspect | Elastic Beanstalk | ECS Fargate | Lambda |
|--------|---|---|---|
| **Setup Time** | 1-2 hours | 2-4 hours | 3-5 hours |
| **Cost** | $20-50/mo | $30-80/mo | $0-20/mo* |
| **Scalability** | Good | Excellent | Limited |
| **WebSocket Support** | ✓ | ✓ | ✗ |
| **Maintenance** | Minimal | Low | None |
| **Learning Curve** | Low | Medium | Medium |
| **Production Ready** | ✓ | ✓✓ | ✗ (for this app) |

*Lambda cost varies; cold starts may impact multiplayer experience.

---

## 🔐 SECURITY HARDENING FOR AWS

1. **RDS Database**:
   - [ ] Enable encryption at rest (AWS KMS)
   - [ ] Enable encryption in transit (SSL/TLS)
   - [ ] Restrict security group to only allow traffic from ECS/EB
   - [ ] Enable automated backups (7-30 day retention)
   - [ ] Enable CloudTrail logging for audit

2. **Application**:
   - [ ] Use AWS Secrets Manager for SECRET_KEY & DB passwords
   - [ ] Enable WAF (Web Application Firewall) on ALB
   - [ ] Use AWS Certificate Manager for HTTPS (free)
   - [ ] Set restrictive ALLOWED_ORIGINS

3. **IAM**:
   - [ ] Create least-privilege IAM role for ECS/EB tasks
   - [ ] Enable MFA for AWS account
   - [ ] Rotate access keys regularly

4. **Monitoring**:
   - [ ] Enable CloudWatch alarms for CPU, memory, error rates
   - [ ] Set up SNS notifications for alarms
   - [ ] Enable VPC Flow Logs for network monitoring

---

## 🚨 TROUBLESHOOTING COMMON AWS DEPLOYMENT ISSUES

### WebSocket Connection Issues
**Problem**: WebSockets fail on ALB  
**Solution**: Enable `stickiness` on ALB target group (cookie-based or duration-based)

### Database Connection Timeouts
**Problem**: Connection pool exhaustion  
**Solution**: Increase `pool_size` in SQLAlchemy config, ensure RDS security group allows traffic

### Slow First Request (Cold Start)
**Problem**: ECS tasks take time to start  
**Solution**: Set up CloudWatch health checks with longer grace period

### Docker Image Size Issues
**Problem**: Slow deployment/cold start  
**Solution**: Use Python 3.11-slim (already in use), remove unnecessary dependencies

---

## 📈 NEXT STEPS FOR PRODUCTION

### Week 1: Deploy to AWS Staging
1. Set up staging RDS instance
2. Deploy to EB or ECS in staging environment
3. Run full test suite
4. Load test multiplayer features

### Week 2: Production Deployment
1. Set up production RDS with backups
2. Deploy to production AWS environment
3. Set up monitoring & alerting
4. Configure DNS (Route 53)
5. Enable CloudFront for static assets

### Week 3+: Post-Deployment
1. Monitor logs and metrics
2. Optimize database queries
3. Set up automated backups
4. Plan for scaling if needed

---

## 📚 USEFUL AWS RESOURCES

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [ECS Fargate Launch Types](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html)
- [RDS PostgreSQL Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

## ✅ SUMMARY

**Current Status**: Application is production-ready for immediate AWS deployment  
**Recommended Path**: AWS Elastic Beanstalk for speed, ECS Fargate for scalability  
**Estimated Time**: 1-2 hours with EB, 2-4 hours with ECS  
**Estimated Cost**: $20-80/month depending on traffic  
**Next Action**: Generate SECRET_KEY and follow "AWS Deployment Quick Start" above
