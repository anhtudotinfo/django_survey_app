# Hướng Dẫn Deploy Django Survey App với Docker Compose + Nginx

## 📋 Mục Lục

1. [Chuẩn Bị](#chuẩn-bị)
2. [Cấu Hình Ban Đầu](#cấu-hình-ban-đầu)
3. [Build và Deploy](#build-và-deploy)
4. [Cấu Hình SSL (Sau Khi Có Domain)](#cấu-hình-ssl)
5. [Quản Lý và Bảo Trì](#quản-lý-và-bảo-trì)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Chuẩn Bị

### 1. **Yêu Cầu Hệ Thống**

**Server:**
- Ubuntu 20.04 hoặc mới hơn (hoặc CentOS 7+)
- RAM: Tối thiểu 2GB (khuyến nghị 4GB)
- CPU: 2 cores trở lên
- Disk: 20GB trở lên
- IP Public

**Software:**
- Docker: v20.10+
- Docker Compose: v2.0+
- Git

### 2. **Cài Đặt Docker và Docker Compose**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Logout and login again for group changes
```

---

## ⚙️ Cấu Hình Ban Đầu

### 1. **Clone Project**

```bash
# Clone repository
git clone https://github.com/your-repo/django_survey_app.git
cd django_survey_app

# Or upload your code via SCP/SFTP
```

### 2. **Tạo File Environment**

```bash
# Copy example env file
cp .env.example .env

# Edit environment variables
nano .env
```

**Cấu hình .env:**
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-generate-new-one

# Database Settings
DB_NAME=survey_db
DB_USER=survey_user
DB_PASSWORD=StrongPassword123!@#

# Domain Settings (Tạm thời dùng IP trước)
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_SERVER_IP

# Email Settings (Optional - for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Generate SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. **Cập Nhật Settings.py**

Đảm bảo `moi/settings.py` có config sau:

```python
import os
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 🏗️ Build và Deploy

### 1. **Build Docker Images**

```bash
# Build images
docker-compose build

# Verify images
docker images | grep survey
```

### 2. **Start Services**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Expected output:
# NAME            COMMAND                  STATUS
# survey_db       "docker-entrypoint.s…"   Up (healthy)
# survey_web      "gunicorn --bind 0.0…"   Up (healthy)
# survey_nginx    "/docker-entrypoint.…"   Up (healthy)
```

### 3. **Run Migrations**

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. **Verify Deployment**

```bash
# Check logs
docker-compose logs -f web
docker-compose logs -f nginx

# Test application
curl http://YOUR_SERVER_IP/

# Open in browser
http://YOUR_SERVER_IP/
```

---

## 🔒 Cấu Hình SSL

### Bước 1: **Trỏ Domain về Server**

**A. Mua domain (nếu chưa có):**
- Namecheap, GoDaddy, PA Domain, etc.

**B. Cấu hình DNS:**
```
Type    Name    Value               TTL
A       @       YOUR_SERVER_IP      3600
A       www     YOUR_SERVER_IP      3600
```

**C. Verify DNS:**
```bash
# Check DNS propagation
nslookup your-domain.com
ping your-domain.com

# Should return your server IP
```

### Bước 2: **Cập Nhật ALLOWED_HOSTS**

```bash
# Edit .env file
nano .env

# Update ALLOWED_HOSTS
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_SERVER_IP,your-domain.com,www.your-domain.com

# Restart web service
docker-compose restart web
```

### Bước 3: **Setup SSL với Let's Encrypt**

**Option 1: Tự động (Recommended)**

```bash
# Run SSL setup script
./setup-ssl.sh your-domain.com

# Script sẽ tự động:
# 1. Cập nhật nginx config
# 2. Get SSL certificate từ Let's Encrypt
# 3. Enable HTTPS
# 4. Reload nginx
```

**Option 2: Thủ công**

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Get SSL certificate
docker run -it --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email admin@your-domain.com \
    --agree-tos \
    -d your-domain.com \
    -d www.your-domain.com

# Copy certificates
mkdir -p nginx/ssl
cp nginx/ssl/live/your-domain.com/fullchain.pem nginx/ssl/fullchain.pem
cp nginx/ssl/live/your-domain.com/privkey.pem nginx/ssl/privkey.pem

# Update nginx config
nano nginx/conf.d/default.conf
# Uncomment HTTPS server block
# Update server_name to your domain

# Start nginx
docker-compose up -d nginx
```

### Bước 4: **Verify SSL**

```bash
# Test HTTPS
curl https://your-domain.com/

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Online checker
# https://www.ssllabs.com/ssltest/
```

### Bước 5: **Auto-Renew SSL (Cron Job)**

```bash
# Create renewal script
cat > renew-ssl.sh <<'EOF'
#!/bin/bash
docker run --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    certbot/certbot renew \
    && docker-compose restart nginx
EOF

chmod +x renew-ssl.sh

# Add to crontab (runs every Monday at 3am)
crontab -e

# Add this line:
0 3 * * 1 cd /path/to/django_survey_app && ./renew-ssl.sh >> /var/log/ssl-renew.log 2>&1
```

---

## 🛠️ Quản Lý và Bảo Trì

### **Xem Logs**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 web
```

### **Restart Services**

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart nginx
```

### **Update Code**

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### **Backup Database**

```bash
# Create backup
docker-compose exec db pg_dump -U survey_user survey_db > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20250102.sql | docker-compose exec -T db psql -U survey_user survey_db
```

### **Scale Application**

```bash
# Scale web workers
docker-compose up -d --scale web=3

# Update nginx upstream to load balance
```

### **Monitor Resources**

```bash
# Check container stats
docker stats

# Check disk usage
docker system df

# Clean up unused images/containers
docker system prune -a
```

---

## 🐛 Troubleshooting

### **Problem 1: Container Won't Start**

```bash
# Check logs
docker-compose logs web

# Common issues:
# - Port already in use
# - Database connection failed
# - Missing environment variables

# Solution:
docker-compose down
docker-compose up -d
```

### **Problem 2: 502 Bad Gateway**

```bash
# Check if web container is running
docker-compose ps

# Check web logs
docker-compose logs web

# Restart web service
docker-compose restart web
```

### **Problem 3: Static Files Not Loading**

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx config
docker-compose exec nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

### **Problem 4: SSL Certificate Error**

```bash
# Check certificate files
ls -la nginx/ssl/

# Re-generate certificate
docker-compose stop nginx
./setup-ssl.sh your-domain.com
```

### **Problem 5: Database Connection Error**

```bash
# Check database status
docker-compose exec db psql -U survey_user -d survey_db

# Reset database
docker-compose down -v  # WARNING: This deletes data!
docker-compose up -d
docker-compose exec web python manage.py migrate
```

---

## 📊 Production Checklist

### **Security:**
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY generated
- [ ] Strong database password
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL certificate installed
- [ ] Firewall configured (UFW/iptables)
- [ ] Only ports 80, 443, 22 open

### **Performance:**
- [ ] Gunicorn workers configured (3-5)
- [ ] Nginx gzip enabled
- [ ] Static files served by Nginx
- [ ] Database indexes created
- [ ] Redis caching (optional)

### **Monitoring:**
- [ ] Log rotation configured
- [ ] Backup cron job setup
- [ ] SSL renewal cron job setup
- [ ] Uptime monitoring (UptimeRobot, etc.)
- [ ] Error tracking (Sentry, optional)

### **Backup:**
- [ ] Database backup script
- [ ] Media files backup
- [ ] Config files backup
- [ ] Off-site backup storage

---

## 📞 Support Commands

```bash
# Access Django shell
docker-compose exec web python manage.py shell

# Access database shell
docker-compose exec db psql -U survey_user survey_db

# Access container bash
docker-compose exec web bash
docker-compose exec nginx sh

# View container logs in real-time
docker-compose logs -f --tail=100

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes data)
docker-compose down -v

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎯 Quick Reference

### **Start Everything:**
```bash
docker-compose up -d && docker-compose logs -f
```

### **Stop Everything:**
```bash
docker-compose down
```

### **Update Application:**
```bash
git pull && docker-compose down && docker-compose build && docker-compose up -d
```

### **Backup Database:**
```bash
docker-compose exec db pg_dump -U survey_user survey_db > backup_$(date +%Y%m%d).sql
```

### **View Logs:**
```bash
docker-compose logs -f web nginx
```

---

**🎉 Deployment Complete!**

Your Django Survey App is now running in production with:
- ✅ Docker containers
- ✅ PostgreSQL database
- ✅ Nginx reverse proxy
- ✅ SSL ready (after domain setup)
- ✅ Auto-restart on failure
- ✅ Production-ready configuration

**Next Steps:**
1. Test application functionality
2. Setup domain and SSL
3. Configure backup schedule
4. Setup monitoring
5. Print QR codes for distribution!

**For Công An Phường An Khê - Ready to serve! 🏛️**
