# Django Survey Application

## Overview
A comprehensive Django-based survey management system designed for Công An Phường An Khê (Quận Thanh Khê, TP. Đà Nẵng). This application provides powerful features for creating, managing, and analyzing surveys with support for conditional logic, file uploads, QR code generation, and response analytics.

## Project Information
- **Framework**: Django 5.2.7
- **Language**: Python 3.11
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Purpose**: Survey management and data collection system
- **Static File Serving**: Whitenoise with compression (for production)

## Key Features
### Core Survey Features
- Dynamic survey creation with multiple sections
- Conditional logic and branching
- Support for various question types
- File uploads (images, documents, PDFs)
- QR code generation for easy survey access
- Response management and analytics
- CSV export with advanced filtering
- Device info capture (IP, browser, OS)

### Admin Features
- Modern Jazzmin-themed admin interface
- Survey management dashboard
- Response analytics and statistics
- User management
- Data export capabilities

### Guest Features
- Anonymous survey viewing (configurable)
- Guest survey submissions
- QR code scanning for easy access
- Mobile-friendly interface

## Project Structure
```
django_survey_app/
├── accounts/           # User account management
├── djf_surveys/        # Main survey application
│   ├── admins/        # Admin configurations
│   ├── static/        # Static files (CSS, JS, images)
│   ├── templates/     # Survey templates
│   ├── models.py      # Database models
│   ├── views.py       # View controllers
│   └── urls.py        # URL routing
├── moi/               # Django project settings
│   ├── settings.py    # Development settings
│   ├── settings_production.py  # Production settings
│   ├── urls.py        # Main URL configuration
│   └── wsgi.py        # WSGI application
├── templates/         # Global templates
├── static/            # Global static files
├── media/             # User uploaded files
├── staticfiles/       # Collected static files
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Configuration

### Environment Variables
The application uses environment variables via python-decouple. The `.env` file contains:
- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Enable/disable debug mode (True/False, properly cast to boolean)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (e.g., 'localhost,127.0.0.1,.replit.dev,.pike.replit.dev')
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database configuration

### Django Settings
- **ALLOWED_HOSTS**: Configured via environment variable (comma-separated list), defaults to localhost/testserver
- **DEBUG**: Properly configured with boolean casting (DEBUG=False works correctly in production)
- **Database**: Currently using SQLite for simplicity
- **Static Files**: Collected to `staticfiles/` directory, served by Whitenoise with compression in production
- **Media Files**: Uploaded to `media/` directory
- **File Upload Limits**: 10MB max, supports images, PDFs, Word, Excel

## Development Setup

### Prerequisites
- Python 3.11 installed via Replit modules
- All dependencies installed from requirements.txt

### Running the Application
The application runs on port 5000 using Django's development server:
```bash
python manage.py runserver 0.0.0.0:5000
```

### Common Commands
```bash
# Database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver 0.0.0.0:5000
```

## Deployment

### Replit Deployment
The application is configured for Replit deployment using:
- **Deployment Type**: Autoscale
- **Production Server**: Gunicorn WSGI server
- **Command**: `gunicorn --bind=0.0.0.0:5000 --reuse-port moi.wsgi:application`

### Production Considerations
1. Set `DEBUG=False` in .env
2. Update `ALLOWED_HOSTS` with actual domain
3. Consider migrating to PostgreSQL for production
4. Configure proper static file serving
5. Set up SSL/HTTPS
6. Enable security headers (already configured in settings_production.py)

## Dependencies
- **Django 5.0.6+**: Web framework
- **django-jazzmin**: Modern admin theme
- **django-crispy-forms**: Enhanced form rendering
- **crispy-bootstrap5**: Bootstrap 5 support
- **django-extensions**: Developer tools
- **Pillow**: Image processing
- **qrcode**: QR code generation
- **psycopg2-binary**: PostgreSQL adapter
- **python-slugify**: URL slug generation
- **django-phonenumber-field**: Phone number validation
- **gunicorn**: Production WSGI server
- **whitenoise**: Static file serving for production
- **python-decouple**: Environment variable management

## URLs and Access
- **Homepage**: `/` - Survey list
- **Admin Panel**: `/admin/` - Admin interface
- **QR Codes**: `/qr/<survey-slug>/` - QR code access
- **User Accounts**: `/accounts/` - Login, register, profile

## Recent Changes (Replit Import Setup)
- Installed Python 3.11 and all dependencies
- Created comprehensive requirements.txt with all required packages
- **Security**: Fixed DEBUG configuration to use boolean casting (prevents debug mode in production)
- **Security**: Changed ALLOWED_HOSTS to use environment variable instead of wildcard (prevents host header injection)
- **Production**: Added Whitenoise middleware with compression for production static file serving
- Configured workflow for port 5000 (required for Replit webview)
- Set up deployment configuration with Gunicorn for autoscale deployment
- Updated .env.example with ALLOWED_HOSTS configuration examples
- Added myenv/ to .gitignore
- Collected static files for production readiness
- Corrected Django version documentation (5.2.7)

## User Preferences
None specified yet.

## Notes
- The application comes with extensive documentation (multiple .md files in root)
- QR codes display full domain on homepage and detail pages
- Modern UI with Tailwind CSS and Alpine.js
- Vietnamese localization available
- Security features include CSRF protection, XSS prevention, secure cookies
