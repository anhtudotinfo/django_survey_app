# Security Warnings - Production Deployment

## ⚠️ Current Security Issues

When running `python manage.py check --deploy`, the following security warnings are identified:

### Critical (Must Fix Before Production)

#### 1. DEBUG = True (security.W018)
**Issue**: DEBUG is set to True in deployment  
**Risk**: Exposes sensitive information in error pages  
**Fix**:
```python
# In moi/settings.py
DEBUG = False  # For production only
```

#### 2. ALLOWED_HOSTS Empty (security.W020)
**Issue**: ALLOWED_HOSTS must not be empty in deployment  
**Risk**: Host header attacks  
**Fix**:
```python
# In moi/settings.py
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'your-server-ip']
```

#### 3. SECRET_KEY Weak (security.W009)
**Issue**: SECRET_KEY has less than 50 characters or is auto-generated  
**Risk**: Security features vulnerable to attack  
**Fix**:
```python
# Generate a strong secret key
import secrets
SECRET_KEY = secrets.token_urlsafe(50)

# Or use environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-for-dev-only')
```

### High Priority (Should Fix)

#### 4. SECURE_SSL_REDIRECT = False (security.W008)
**Issue**: Site not automatically redirecting to HTTPS  
**Risk**: Data transmitted over insecure connection  
**Fix**:
```python
# In moi/settings.py (for production)
SECURE_SSL_REDIRECT = True
```

#### 5. SESSION_COOKIE_SECURE = False (security.W012)
**Issue**: Session cookies not marked as secure-only  
**Risk**: Session hijacking via network sniffing  
**Fix**:
```python
# In moi/settings.py (for production)
SESSION_COOKIE_SECURE = True
```

#### 6. CSRF_COOKIE_SECURE = False (security.W016)
**Issue**: CSRF cookies not marked as secure-only  
**Risk**: CSRF token theft via network sniffing  
**Fix**:
```python
# In moi/settings.py (for production)
CSRF_COOKIE_SECURE = True
```

### Medium Priority (Recommended)

#### 7. SECURE_HSTS_SECONDS Not Set (security.W004)
**Issue**: HTTP Strict Transport Security not enabled  
**Risk**: Vulnerable to SSL stripping attacks  
**Fix**:
```python
# In moi/settings.py (for production)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 📝 Recommended Production Settings

### Create Production Settings File

**Option 1: Environment-based settings**

```python
# In moi/settings.py

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-CHANGE-THIS')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

**Option 2: Separate settings files**

```bash
# Create settings directory
mkdir moi/settings
mv moi/settings.py moi/settings/base.py

# Create development settings
# moi/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = 'dev-secret-key'

# Create production settings
# moi/settings/prod.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## ✅ Pre-Deployment Security Checklist

### Critical Security Items
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Generate strong SECRET_KEY (50+ characters)
- [ ] Store SECRET_KEY in environment variable
- [ ] Set SECURE_SSL_REDIRECT = True
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Set CSRF_COOKIE_SECURE = True

### Additional Security Items
- [ ] Configure HSTS headers
- [ ] Verify HTTPS/SSL certificate installed
- [ ] Test all security settings
- [ ] Remove any hardcoded credentials
- [ ] Check database credentials secure
- [ ] Verify file upload security
- [ ] Test CSRF protection
- [ ] Test authentication/authorization

---

## 🔧 Environment Variables Setup

### Development (.env.dev)
```bash
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Production (.env.prod)
```bash
DEBUG=False
SECRET_KEY=your-super-secret-production-key-50-plus-characters-long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Using python-decouple
```bash
pip install python-decouple
```

```python
# In moi/settings.py
from decouple import config, Csv

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
```

---

## 🧪 Testing Security Settings

### Test 1: Check DEBUG = False
```bash
# Set DEBUG = False
# Visit a non-existent URL
# Should see generic 404, not detailed error page
```

### Test 2: Check HTTPS Redirect
```bash
# With SECURE_SSL_REDIRECT = True
curl -I http://your-domain.com/
# Should get 301 redirect to https://
```

### Test 3: Check Secure Cookies
```bash
# Open browser developer tools
# Check cookies
# Should see "Secure" flag on sessionid and csrftoken
```

### Test 4: Check HSTS Header
```bash
curl -I https://your-domain.com/
# Should see header:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## 📊 Security Scoring

### Current (Development)
```
Security Score: 3/10 ⚠️

Critical Issues: 3
High Priority: 3
Medium Priority: 1

Status: NOT READY FOR PRODUCTION
```

### Target (Production)
```
Security Score: 10/10 ✅

Critical Issues: 0
High Priority: 0
Medium Priority: 0

Status: PRODUCTION READY
```

---

## 🚀 Quick Fix Script

Create this script to quickly apply production security settings:

```python
# scripts/apply_production_security.py

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure SECRET_KEY"""
    return secrets.token_urlsafe(50)

def update_settings_for_production(settings_file):
    """Update settings.py for production"""
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Generate new secret key
    new_secret = generate_secret_key()
    
    # Prepare production settings
    production_settings = f"""

# Production Security Settings (Auto-generated)
import os

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', '{new_secret}')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
"""
    
    print("Production security settings generated!")
    print(f"\nAdd this to your settings.py:\n{production_settings}")
    print(f"\nSECRET_KEY to use in environment variable:\n{new_secret}")

if __name__ == '__main__':
    settings_path = Path(__file__).parent.parent / 'moi' / 'settings.py'
    update_settings_for_production(settings_path)
```

---

## 📞 Support

For security questions or concerns, refer to:
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SECURITY_REVIEW.md](SECURITY_REVIEW.md) - Complete security checklist

---

**Document Version**: 1.0  
**Last Updated**: October 31, 2025  
**Priority**: HIGH - Must address before production deployment
