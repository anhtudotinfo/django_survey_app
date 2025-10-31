# Deployment Checklist - Survey Application

## 📋 Pre-Deployment Checklist

### ✅ Code & Testing
- [x] All migrations created and tested
- [x] Migration rollback tested successfully
- [x] All 34 automated tests passing (100%)
- [x] Code review completed
- [ ] Manual QA testing completed
- [ ] Performance testing with realistic data
- [ ] Security review completed
- [x] Documentation updated

### ✅ Database
- [x] Migrations applied to dev database
- [ ] Backup of current production database created
- [ ] Test migrations on copy of production database
- [ ] Verify backward compatibility with existing data
- [x] Database indexes created (automatic via migrations)
- [ ] Check database size and plan for growth

### ✅ File Storage
- [x] MEDIA_ROOT configured
- [x] MEDIA_URL configured
- [ ] File upload directory exists with correct permissions
- [ ] Storage space available (estimate: 1GB per 1000 file uploads)
- [ ] Consider cloud storage (S3) for production
- [x] File cleanup commands tested

### ✅ Settings Configuration
- [x] SURVEY_FILE_UPLOAD_MAX_SIZE set (default: 10MB)
- [x] SURVEY_FILE_ALLOWED_TYPES configured
- [x] SURVEY_DRAFT_EXPIRY_DAYS set (default: 30)
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS configured
- [ ] SECRET_KEY properly set (not in version control)
- [ ] Database credentials secure

### ✅ Cron Jobs
- [ ] Cron jobs configured (see CRON_SETUP.md)
- [ ] Test cleanup_expired_drafts command
- [ ] Test cleanup_orphaned_files command
- [ ] Log directories created
- [ ] Log rotation configured

---

## 🚀 Deployment Steps

### Phase 1: Preparation (Before Deployment)

#### 1.1 Backup Everything
```bash
# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# OR for SQLite
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup code (if not in git)
tar -czf code_backup_$(date +%Y%m%d).tar.gz \
    --exclude='media' \
    --exclude='venv' \
    --exclude='*.pyc' \
    .
```

#### 1.2 Run Final Tests
```bash
# Run all tests
python manage.py test djf_surveys.tests

# Check for issues
python manage.py check --deploy

# Verify migrations
python manage.py showmigrations
```

#### 1.3 Review Changes
```bash
# Review git status
git status

# Review recent commits
git log --oneline -10

# Check for uncommitted changes
git diff
```

---

### Phase 2: Deployment (Execute in Order)

#### 2.1 Stop Application (if running)
```bash
# Stop application server
sudo systemctl stop gunicorn  # or your app server

# OR for development
# Just stop manage.py runserver
```

#### 2.2 Pull Latest Code
```bash
# Pull from repository
git pull origin main

# Or copy new files to server
```

#### 2.3 Update Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install/update packages
pip install -r requirements.txt

# Verify installations
pip list
```

#### 2.4 Run Migrations
```bash
# Check pending migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Verify all applied
python manage.py showmigrations | grep "\[ \]"  # Should be empty
```

#### 2.5 Collect Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

#### 2.6 Create Media Directories
```bash
# Create media directory if not exists
mkdir -p media/survey_uploads

# Set permissions
chmod 755 media
chmod 755 media/survey_uploads
chown -R www-data:www-data media  # Adjust user/group as needed
```

#### 2.7 Verify Configuration
```bash
# Check system
python manage.py check --deploy

# Test database connection
python manage.py shell -c "from django.db import connection; connection.cursor()"
```

#### 2.8 Start Application
```bash
# Start application server
sudo systemctl start gunicorn  # or your app server

# Verify running
sudo systemctl status gunicorn
```

#### 2.9 Setup Cron Jobs
```bash
# Edit crontab
crontab -e

# Add cleanup jobs (see CRON_SETUP.md)
0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py cleanup_expired_drafts >> /var/log/django/cleanup_drafts.log 2>&1
0 3 * * 0 cd /path/to/project && /path/to/venv/bin/python manage.py cleanup_orphaned_files >> /var/log/django/cleanup_files.log 2>&1

# Verify cron installed
crontab -l
```

---

### Phase 3: Verification (Post-Deployment)

#### 3.1 Smoke Tests
```bash
# Check homepage loads
curl -I http://your-domain.com/

# Check admin loads
curl -I http://your-domain.com/moi-admin/

# Check survey loads (replace slug)
curl -I http://your-domain.com/create/test-survey/
```

#### 3.2 Admin Verification
1. Login to admin: http://your-domain.com/moi-admin/
2. Check all models visible:
   - Surveys ✓
   - Sections ✓
   - Questions ✓
   - Branch Rules ✓
   - Draft Responses ✓
   - User Answers ✓
3. Test creating a section
4. Test creating a question with file upload type
5. Test creating a branch rule

#### 3.3 User Flow Verification
1. Open survey: http://your-domain.com/create/{slug}/
2. Fill first section
3. Click "Next" → Verify navigation
4. Test "Save Draft" button
5. Close browser and return
6. Verify "Resume draft" banner shows
7. Complete and submit survey
8. Verify success page shows

#### 3.4 File Upload Verification
1. Create question with type "File Upload"
2. Upload a test PDF (< 10MB)
3. Submit survey
4. Check admin → Answers
5. Verify file link works
6. Click to download → File should download

#### 3.5 Branch Logic Verification
1. Create section with branch rule
2. Fill survey with condition met
3. Verify correct section shown (skip/jump)
4. Fill survey with condition not met
5. Verify sequential navigation

#### 3.6 System Health
```bash
# Check logs for errors
tail -50 /var/log/django/django.log
tail -50 /var/log/nginx/error.log  # if using nginx

# Check disk space
df -h

# Check process running
ps aux | grep gunicorn  # or your app server

# Check database size
python manage.py dbshell -c "SELECT pg_size_pretty(pg_database_size('your_db'));"  # PostgreSQL
# OR
ls -lh db.sqlite3  # SQLite
```

---

## 🔄 Rollback Plan

### If Deployment Fails

#### Quick Rollback (Code)
```bash
# Stop application
sudo systemctl stop gunicorn

# Revert to previous commit
git reset --hard HEAD~1
# OR checkout previous tag
git checkout v1.0.0

# Rollback migrations if needed
python manage.py migrate djf_surveys 0022

# Restart application
sudo systemctl start gunicorn
```

#### Full Rollback (Database)
```bash
# Stop application
sudo systemctl stop gunicorn

# Restore database backup
# For SQLite:
cp db.sqlite3.backup_20251031 db.sqlite3

# For PostgreSQL:
# psql your_db < backup_20251031.sql

# Restore media files if needed
tar -xzf media_backup_20251031.tar.gz

# Revert code
git reset --hard HEAD~1

# Restart application
sudo systemctl start gunicorn
```

---

## 📊 Monitoring & Alerts

### What to Monitor

#### Application Health
- [ ] Application server status
- [ ] Response time < 2 seconds
- [ ] Error rate < 1%
- [ ] Memory usage stable

#### Database
- [ ] Database connection pool
- [ ] Query performance
- [ ] Database size growth
- [ ] Draft response count

#### File Storage
- [ ] Disk space usage
- [ ] Upload success rate
- [ ] File download latency
- [ ] Orphaned files count

#### Cron Jobs
- [ ] Cleanup jobs running
- [ ] No errors in logs
- [ ] Expected deletion counts

### Monitoring Tools
```bash
# Application monitoring
tail -f /var/log/django/django.log

# System monitoring
htop
df -h
du -sh media/

# Database monitoring
python manage.py dbshell
> SELECT COUNT(*) FROM djf_surveys_draftresponse;
> SELECT COUNT(*) FROM djf_surveys_answer WHERE file_value IS NOT NULL;
```

---

## 🔐 Security Checklist

### Pre-Deployment Security
- [ ] DEBUG = False in production
- [ ] SECRET_KEY is secure and not in version control
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database credentials not hardcoded
- [ ] Static file permissions correct (644)
- [ ] Media file permissions correct (644)
- [ ] Directories have correct permissions (755)

### File Upload Security
- [x] File type validation enabled
- [x] File size limits configured
- [x] File name sanitization enabled
- [x] File access control implemented
- [ ] Consider virus scanning integration
- [ ] Monitor for suspicious uploads

### Authentication Security
- [ ] Strong admin passwords
- [ ] HTTPS enabled (SSL/TLS)
- [ ] CSRF protection enabled (Django default)
- [ ] XSS protection enabled
- [ ] Session security configured

### Data Security
- [x] Draft responses expire automatically
- [x] User/session isolation in drafts
- [ ] Regular backups scheduled
- [ ] Sensitive data not logged
- [ ] File cleanup runs regularly

---

## 📝 Post-Deployment Tasks

### Immediate (Day 1)
- [ ] Monitor error logs for 1 hour
- [ ] Test all critical flows
- [ ] Verify cron jobs scheduled
- [ ] Send test survey to team
- [ ] Document any issues

### Short Term (Week 1)
- [ ] Monitor daily for errors
- [ ] Check draft cleanup running
- [ ] Check file cleanup running
- [ ] Review user feedback
- [ ] Performance monitoring

### Medium Term (Month 1)
- [ ] Review storage usage
- [ ] Review database size
- [ ] Optimize if needed
- [ ] Update documentation
- [ ] Plan next features

---

## 🎯 Success Criteria

### Deployment Successful If:
- ✅ Application starts without errors
- ✅ Admin interface accessible and functional
- ✅ Existing surveys still work (backward compatibility)
- ✅ New features accessible (sections, file upload, drafts)
- ✅ No critical errors in logs
- ✅ Database migrations applied successfully
- ✅ File uploads working
- ✅ Cron jobs scheduled
- ✅ Users can complete surveys
- ✅ Response time acceptable (< 2 sec)

### Red Flags (Abort Deployment):
- ❌ Migrations fail
- ❌ Application won't start
- ❌ Critical errors in logs
- ❌ Existing surveys broken
- ❌ Data loss detected
- ❌ Security vulnerabilities exposed
- ❌ Database corruption

---

## 📞 Support & Contacts

### Emergency Contacts
- **Tech Lead**: [name/email]
- **DevOps**: [name/email]
- **DBA**: [name/email]

### Resources
- **Documentation**: `/docs/` folder
- **Logs**: `/var/log/django/`
- **Backups**: `/backups/`
- **Git Repo**: [repository URL]

### Quick Commands Reference
```bash
# Check status
sudo systemctl status gunicorn
python manage.py check

# View logs
tail -f /var/log/django/django.log

# Database shell
python manage.py dbshell

# Run tests
python manage.py test djf_surveys.tests

# Cleanup commands
python manage.py cleanup_expired_drafts
python manage.py cleanup_orphaned_files --dry-run
```

---

## ✅ Final Verification

Before marking deployment complete, verify:

- [ ] All items in "Pre-Deployment Checklist" checked
- [ ] All steps in "Deployment Steps" completed
- [ ] All tests in "Verification" passed
- [ ] Monitoring configured and working
- [ ] Rollback plan tested and ready
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Support ready for user questions

**Deployment Status**: [ ] Ready / [ ] In Progress / [ ] Complete / [ ] Rolled Back

**Deployment Date**: _________________

**Deployed By**: _________________

**Notes**: 
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 📈 Performance Benchmarks

Expected performance after deployment:

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Page Load | < 1s | < 2s | > 2s |
| Survey Submit | < 1s | < 2s | > 2s |
| File Upload (10MB) | < 5s | < 10s | > 10s |
| Admin Load | < 1s | < 2s | > 2s |
| Database Queries | < 50/page | < 100/page | > 100/page |

Monitor these metrics in first week and optimize if needed.

---

**Document Version**: 1.0  
**Last Updated**: October 31, 2025  
**Status**: Ready for Use
