# 🚀 Django Survey App - Production Deployment

## Công An Phường An Khê - Hệ Thống Thu Thập Thông Tin

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-Configured-green)](https://nginx.org/)
[![SSL](https://img.shields.io/badge/SSL-Ready-success)](https://letsencrypt.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

---

## 📖 Tài Liệu

Dự án này có tài liệu đầy đủ cho deployment:

### 🚀 Quick Start
📄 **[QUICK_START.md](QUICK_START.md)** - Deploy trong 5 phút!
- Bước 1: Chuẩn bị server
- Bước 2: Upload code
- Bước 3: Cấu hình .env
- Bước 4: Deploy!
- Bước 5: Setup SSL

### 📚 Complete Guide
📄 **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Hướng dẫn chi tiết
- Chuẩn bị hệ thống
- Cấu hình Docker & Nginx
- SSL với Let's Encrypt
- Quản lý & bảo trì
- Troubleshooting

### 📊 Summary
📄 **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Tóm tắt deployment
- Architecture overview
- Configuration details
- Management commands
- Security checklist

---

## 🏗️ Architecture

```
Internet → Nginx (SSL) → Gunicorn → Django → PostgreSQL
              ↓
         Static Files
              ↓
         Media Files
```

**Components:**
- **Nginx**: Reverse proxy, SSL termination, static files
- **Gunicorn**: WSGI server (3 workers)
- **Django**: Survey application
- **PostgreSQL**: Database (persistent data)

---

## ⚡ Quick Commands

### Deploy
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

### Manage
```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart web

# Stop
docker-compose down

# Backup database
docker-compose exec db pg_dump -U survey_user survey_db > backup.sql
```

### SSL Setup
```bash
./setup-ssl.sh your-domain.com
```

---

## 📁 Project Structure

```
django_survey_app/
├── 🐳 Docker Configuration
│   ├── Dockerfile                  # Django container
│   ├── docker-compose.yml          # Production setup
│   ├── docker-compose.dev.yml      # Development override
│   └── .dockerignore               # Exclude files
│
├── 🌐 Nginx Configuration
│   ├── nginx/nginx.conf            # Main config
│   ├── nginx/conf.d/default.conf   # Site config
│   └── nginx/ssl/                  # SSL certificates
│
├── ⚙️ Django Application
│   ├── moi/settings.py             # Development settings
│   ├── moi/settings_production.py  # Production settings
│   ├── djf_surveys/                # Survey app
│   └── manage.py                   # Django management
│
├── 📜 Scripts
│   └── setup-ssl.sh                # Automated SSL setup
│
├── 📚 Documentation
│   ├── README_DEPLOYMENT.md        # This file
│   ├── QUICK_START.md              # 5-minute guide
│   ├── DEPLOYMENT_GUIDE.md         # Complete guide
│   ├── DEPLOYMENT_SUMMARY.md       # Technical summary
│   ├── QR_QUICK_REFERENCE.md       # QR code guide
│   └── MODERN_SURVEY_CARD_REDESIGN.md
│
└── 🔧 Configuration
    ├── .env                        # Environment variables
    ├── .env.example                # Template
    └── requirements.txt            # Python dependencies
```

---

## 🔒 Security Features

✅ **Django Security:**
- DEBUG=False in production
- Strong SECRET_KEY required
- SECURE_SSL_REDIRECT enabled
- HSTS headers (1 year)
- Secure cookies (Session + CSRF)
- X-Frame-Options: DENY

✅ **Server Security:**
- Non-root user in containers
- Read-only volumes where applicable
- Health checks for all services
- Nginx security headers
- SSL/TLS 1.2+ only

✅ **Database Security:**
- PostgreSQL with authentication
- Database in private network
- Connection pooling
- Regular backups recommended

---

## 📊 Features

### Core Features
- ✅ Dynamic survey creation
- ✅ Multi-section surveys
- ✅ Conditional logic/branching
- ✅ File uploads (images, documents)
- ✅ QR code generation with **full domain**
- ✅ Response management
- ✅ CSV export with filters
- ✅ Device info capture (IP, browser, OS)

### QR Code Features (NEW!)
- ✅ **Domain displayed on homepage cards**
- ✅ **Domain displayed on QR detail pages**
- ✅ Modern UI with animations
- ✅ Vietnamese localization
- ✅ Print-ready QR codes
- ✅ Auto-generation with full URLs

### Admin Features
- ✅ Survey management
- ✅ Response analytics
- ✅ Data export (CSV)
- ✅ User management
- ✅ Statistics dashboard

---

## 🌐 URLs

### Production
```
Homepage:    https://your-domain.com/
Admin:       https://your-domain.com/admin/
QR Code:     https://your-domain.com/qr/<survey-slug>/
API:         https://your-domain.com/api/ (if enabled)
```

### Development
```
Homepage:    http://localhost:8000/
Admin:       http://localhost:8000/admin/
```

---

## 🔧 Environment Variables

Required in `.env` file:

```bash
# Django
SECRET_KEY=your-super-secret-key-min-50-chars
DEBUG=False

# Database
DB_NAME=survey_db
DB_USER=survey_user
DB_PASSWORD=strong-password-here

# Domains
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,www.your-domain.com

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📈 Monitoring

### Health Checks
```bash
# Check all services
docker-compose ps

# Check web health
curl -I http://localhost/

# Check database health
docker-compose exec db pg_isready -U survey_user
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db

# View last 100 lines
docker-compose logs --tail=100
```

### Resources
```bash
# Check container resources
docker stats

# Check disk usage
docker system df

# Check volumes
docker volume ls
```

---

## 🔄 Updates & Maintenance

### Update Application
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

### Backup Database
```bash
# Manual backup
docker-compose exec db pg_dump -U survey_user survey_db > backup_$(date +%Y%m%d).sql

# Automated backup (add to cron)
0 2 * * * cd /path/to/app && docker-compose exec db pg_dump -U survey_user survey_db > backup_$(date +\%Y\%m\%d).sql
```

### SSL Certificate Renewal
```bash
# Renew certificate (add to cron)
0 3 * * 1 cd /path/to/app && docker run --rm -v $(pwd)/nginx/ssl:/etc/letsencrypt certbot/certbot renew && docker-compose restart nginx
```

---

## 🆘 Common Issues

### Port Already in Use
```bash
# Find process using port 80
sudo lsof -i :80

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8080:80"  # Use port 8080 instead
```

### Database Connection Failed
```bash
# Check database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Wait for health check
watch docker-compose ps
```

### Static Files Not Loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx config
docker-compose exec nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

---

## 📞 Support & Contact

### Documentation
- 📄 Quick Start: [QUICK_START.md](QUICK_START.md)
- 📄 Complete Guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 📄 Technical Summary: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

### Tools
- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Nginx: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/docs/

### Community
- Django: https://docs.djangoproject.com/
- PostgreSQL: https://www.postgresql.org/docs/

---

## 📝 License

[Your License Here]

---

## 👥 Credits

**Developed For:** Công An Phường An Khê  
**Location:** Quận Thanh Khê, TP. Đà Nẵng  
**Purpose:** Hệ Thống Thu Thập Thông Tin  

---

## ✅ Production Checklist

Before going live:

**Configuration:**
- [ ] `.env` file created with strong passwords
- [ ] `SECRET_KEY` generated (50+ characters)
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database password changed from default
- [ ] Email settings configured (optional)

**Deployment:**
- [ ] Docker and Docker Compose installed
- [ ] Code deployed to server
- [ ] Services started: `docker-compose up -d`
- [ ] Migrations run: `python manage.py migrate`
- [ ] Superuser created
- [ ] Static files collected

**Security:**
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] SSH key authentication enabled
- [ ] SSL certificate installed (after domain setup)
- [ ] HTTPS redirect enabled
- [ ] Regular backups scheduled

**Testing:**
- [ ] Homepage loads correctly
- [ ] Admin panel accessible
- [ ] Survey creation works
- [ ] Survey submission works
- [ ] QR code generation works
- [ ] QR codes show full domain
- [ ] File uploads work
- [ ] CSV export works

**Monitoring:**
- [ ] Health checks passing
- [ ] Logs reviewed for errors
- [ ] Disk space sufficient
- [ ] Backup tested
- [ ] SSL expiry monitored

---

**🎉 Ready to Deploy!**

Follow [QUICK_START.md](QUICK_START.md) to get started in 5 minutes!

---

**Last Updated:** 2025-11-02  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
