# Quick Start - Deploy trong 5 phút

## 🚀 Triển Khai Nhanh

### Bước 1: Chuẩn Bị Server (2 phút)

```bash
# SSH vào server
ssh root@YOUR_SERVER_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version && docker-compose --version
```

### Bước 2: Upload Code (1 phút)

```bash
# Option 1: Git clone
git clone https://github.com/your-repo/django_survey_app.git
cd django_survey_app

# Option 2: Upload via SCP
scp -r django_survey_app root@YOUR_SERVER_IP:/root/
```

### Bước 3: Cấu Hình (.env) (1 phút)

```bash
# Copy và edit .env
cp .env.example .env
nano .env
```

**Sửa các dòng sau:**
```bash
SECRET_KEY=abc123xyz789-CHANGE-THIS  # Generate mới!
DB_PASSWORD=YourStrongPassword123
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_SERVER_IP
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Bước 4: Deploy! (1 phút)

```bash
# Build và start
docker-compose up -d

# Wait for services to be healthy (30 seconds)
watch docker-compose ps

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Bước 5: Verify

```bash
# Test
curl http://YOUR_SERVER_IP/

# Open in browser
http://YOUR_SERVER_IP/
```

**✅ XONG! App đang chạy!**

---

## 🔒 Setup SSL (Sau khi có domain)

### Bước 1: Trỏ Domain

**DNS Settings:**
```
A Record: @ -> YOUR_SERVER_IP
A Record: www -> YOUR_SERVER_IP
```

**Wait for DNS propagation (5-10 minutes):**
```bash
nslookup your-domain.com
```

### Bước 2: Update Config

```bash
# Edit .env
nano .env

# Update ALLOWED_HOSTS
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_IP,your-domain.com,www.your-domain.com

# Restart
docker-compose restart web
```

### Bước 3: Get SSL Certificate

```bash
# Run SSL setup (automated)
./setup-ssl.sh your-domain.com

# Wait 2 minutes...
# Done! Visit: https://your-domain.com
```

**✅ SSL Enabled!**

---

## 📋 Daily Commands

**View logs:**
```bash
docker-compose logs -f
```

**Restart:**
```bash
docker-compose restart
```

**Stop:**
```bash
docker-compose down
```

**Update code:**
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
```

**Backup database:**
```bash
docker-compose exec db pg_dump -U survey_user survey_db > backup.sql
```

---

## 🆘 Troubleshooting

**Container won't start:**
```bash
docker-compose logs web
docker-compose restart web
```

**502 Bad Gateway:**
```bash
docker-compose restart web nginx
```

**Can't access from outside:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

**Database error:**
```bash
docker-compose restart db
docker-compose logs db
```

---

## ✅ Production Checklist

Before going live:

- [ ] DEBUG=False in .env
- [ ] Strong SECRET_KEY generated
- [ ] Strong DB_PASSWORD set
- [ ] ALLOWED_HOSTS configured with domain
- [ ] SSL certificate installed
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] Backup cron job setup
- [ ] Superuser created
- [ ] Test survey creation and submission
- [ ] Test QR code generation and scanning

---

## 📞 Need Help?

**View all logs:**
```bash
docker-compose logs -f --tail=100
```

**Access Django shell:**
```bash
docker-compose exec web python manage.py shell
```

**Access database:**
```bash
docker-compose exec db psql -U survey_user survey_db
```

**Restart everything:**
```bash
docker-compose down && docker-compose up -d
```

---

**🎉 That's it! Your survey app is live!**

Next: Print QR codes and distribute to Công An Phường An Khê! 🏛️
