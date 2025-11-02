# Lấy Internet IP (Public IP)

## Vấn Đề
Khi test local (localhost), IP luôn là `127.0.0.1` hoặc private IP (192.168.x.x, 10.x.x.x).  
Đây **KHÔNG phải** là IP internet thực của bạn.

## Internet IP vs Local IP

### Local IP (Private IP):
- `127.0.0.1` - localhost
- `192.168.x.x` - Local network
- `10.x.x.x` - Private network
- `172.16.x.x` - Private network

### Internet IP (Public IP):
- Ví dụ: `118.70.186.xxx`, `42.115.94.xxx`
- Là IP nhìn thấy từ bên ngoài internet
- IP của router/modem kết nối internet

## Giải Pháp

### ✅ Cách 1: Deploy Lên Server (Recommended)

Khi deploy lên server thật (VPS, cloud hosting), `REMOTE_ADDR` sẽ là IP internet:

```python
# Trên server production
REMOTE_ADDR = '118.70.186.123'  # Real internet IP
```

**Các nền tảng phổ biến:**
- AWS EC2, Azure VM, Google Cloud
- DigitalOcean, Linode, Vultr
- Heroku, PythonAnywhere
- VPS Vietnam (BKHOST, AZDIGI, etc.)

### ✅ Cách 2: Sử Dụng Ngrok (Test Local)

Ngrok tạo tunnel public URL → localhost:

1. **Install ngrok:**
   ```bash
   # Download từ https://ngrok.com/download
   # Hoặc
   sudo snap install ngrok
   ```

2. **Run ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Sẽ nhận được URL:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8000
   ```

4. **Truy cập qua ngrok URL:**
   - Users truy cập: `https://abc123.ngrok.io/create/test/`
   - Ngrok forward về localhost:8000
   - `HTTP_X_FORWARDED_FOR` sẽ chứa internet IP thực!

5. **Check IP captured:**
   ```python
   from djf_surveys.models import UserAnswer
   ua = UserAnswer.objects.latest('created_at')
   print(ua.ip_address)  # Will show real internet IP!
   ```

### ✅ Cách 3: Behind Nginx Reverse Proxy

Nếu dùng nginx làm reverse proxy:

**nginx.conf:**
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
}
```

Django sẽ nhận được IP từ `X-Forwarded-For` header.

### ❌ Cách 4: Gọi External API (Không Khuyến Nghị)

**Lý do không nên:**
- Chậm (phải gọi API)
- Phụ thuộc service bên ngoài
- Có thể bị rate limit
- Tốn bandwidth

**Nhưng nếu cần:**

```python
import requests

def get_public_ip():
    """Get public IP from external service"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=2)
        return response.json()['ip']
    except:
        return None

# In view
public_ip = get_public_ip()
```

**Services có thể dùng:**
- https://api.ipify.org
- https://icanhazip.com
- https://ifconfig.me/ip
- https://checkip.amazonaws.com

## Implementation Hiện Tại

### Code đã có sẵn trong `utils.py`:

```python
def get_client_ip(request):
    """
    Priority order:
    1. HTTP_X_FORWARDED_FOR (from proxy/CDN)
    2. HTTP_X_REAL_IP (from nginx)
    3. REMOTE_ADDR (direct connection)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    return request.META.get('REMOTE_ADDR', 'Unknown')
```

### Khi nào lấy được Internet IP:

| Scenario | IP Type | Example |
|----------|---------|---------|
| Local test (localhost) | Local | 127.0.0.1 |
| Local network | Private | 192.168.1.100 |
| Via ngrok | **Internet** | 118.70.186.xxx ✅ |
| On production server | **Internet** | 42.115.94.xxx ✅ |
| Behind nginx proxy | **Internet** | Real IP ✅ |
| Behind CloudFlare CDN | **Internet** | Real IP ✅ |

## Quick Test với Ngrok

### Bước 1: Install & Setup
```bash
# Install
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Auth (cần account free tại ngrok.com)
ngrok config add-authtoken YOUR_TOKEN
```

### Bước 2: Run
```bash
# Terminal 1: Run Django
python3 manage.py runserver

# Terminal 2: Run ngrok
ngrok http 8000
```

### Bước 3: Test
```bash
# Copy ngrok URL từ terminal (e.g., https://abc123.ngrok.io)
# Truy cập từ điện thoại hoặc máy khác:
https://abc123.ngrok.io/create/test/

# Submit survey
# Check IP:
python3 manage.py shell
>>> from djf_surveys.models import UserAnswer
>>> ua = UserAnswer.objects.latest('created_at')
>>> print(ua.ip_address)
# Sẽ show IP internet thật!
```

## Kiểm Tra IP Hiện Tại

### Check request headers:
```python
# In view, add temporarily:
def post(self, request, *args, **kwargs):
    print("=" * 80)
    print("REQUEST META:")
    print(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')}")
    print(f"HTTP_X_FORWARDED_FOR: {request.META.get('HTTP_X_FORWARDED_FOR')}")
    print(f"HTTP_X_REAL_IP: {request.META.get('HTTP_X_REAL_IP')}")
    print("=" * 80)
    # ... continue normal flow
```

### Check your current internet IP:
```bash
# From terminal
curl ifconfig.me
# Or
curl https://api.ipify.org
```

## Production Setup Recommendations

### 1. Django Settings
```python
# settings.py

# For production behind proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### 2. Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        
        # Forward real IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

### 3. CloudFlare Setup
Nếu dùng CloudFlare CDN, enable:
- Settings → Network → "IP Geolocation"
- Django sẽ nhận IP từ `CF-Connecting-IP` header

Update code:
```python
def get_client_ip(request):
    # CloudFlare
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip
    
    # Existing logic...
```

## Xác Định IP Type

```python
import ipaddress

def is_private_ip(ip):
    """Check if IP is private/local"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback
    except:
        return False

# Usage
ip = get_client_ip(request)
if is_private_ip(ip):
    print("Local/Private IP")
else:
    print("Internet/Public IP")
```

## Tóm Tắt

### Để lấy Internet IP:

✅ **Production:** Deploy lên server → tự động có internet IP  
✅ **Test Local:** Dùng ngrok → có internet IP  
✅ **Behind Proxy:** Config nginx/apache → forward real IP  
✅ **Behind CDN:** CloudFlare/Cloudfront → forward real IP  

❌ **Không nên:** Gọi external API mỗi request  
❌ **Không được:** Test localhost → luôn là local IP  

### Hiện Tại:

Code đã support tất cả scenarios trên. Chỉ cần:
1. Deploy lên server HOẶC
2. Dùng ngrok để test

Sẽ tự động capture internet IP! 🚀

---

**Recommended:** Dùng ngrok để test nhanh, sau đó deploy lên server thật.
