#!/bin/bash

# Setup SSL Certificate with Let's Encrypt
# Usage: ./setup-ssl.sh your-domain.com

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
    echo "Usage: ./setup-ssl.sh your-domain.com"
    exit 1
fi

echo "=========================================="
echo "SSL Setup for: $DOMAIN"
echo "=========================================="

# Step 1: Update nginx config with domain
echo "Step 1: Updating nginx configuration..."
sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/" nginx/conf.d/default.conf

# Step 2: Restart nginx
echo "Step 2: Restarting nginx..."
docker-compose restart nginx

# Step 3: Get SSL certificate using certbot
echo "Step 3: Getting SSL certificate from Let's Encrypt..."
docker run -it --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/certbot:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Step 4: Copy certificates to nginx ssl directory
echo "Step 4: Setting up SSL certificates..."
mkdir -p nginx/ssl
cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/fullchain.pem
cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/privkey.pem

# Step 5: Enable HTTPS in nginx config
echo "Step 5: Enabling HTTPS configuration..."
cat > nginx/conf.d/default.conf <<EOF
# Upstream to Django application
upstream django {
    server web:8000;
}

# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
EOF

# Step 6: Reload nginx
echo "Step 6: Reloading nginx with SSL configuration..."
docker-compose restart nginx

echo "=========================================="
echo "SSL Setup Complete!"
echo "Your site is now available at: https://$DOMAIN"
echo "=========================================="
