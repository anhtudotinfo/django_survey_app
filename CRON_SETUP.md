# Cron Job Setup for Survey Application

This document describes how to set up automated cleanup tasks for the survey application.

## Overview

The survey application includes two management commands that should be run periodically to maintain system health:

1. **cleanup_expired_drafts** - Removes expired draft survey responses
2. **cleanup_orphaned_files** - Removes uploaded files that are no longer referenced in the database

## Prerequisites

- Django project deployed and accessible
- Cron or similar task scheduler available
- Python virtual environment (if used)
- Proper file permissions for the Django user

## Cron Jobs Configuration

### 1. Edit Crontab

Open the crontab editor for the user that runs your Django application:

```bash
crontab -e
```

### 2. Add Cleanup Jobs

Add the following lines to your crontab:

```cron
# Clean up expired draft survey responses daily at 2:00 AM
0 2 * * * cd /path/to/django_survey_app && /path/to/venv/bin/python manage.py cleanup_expired_drafts >> /var/log/django/cleanup_drafts.log 2>&1

# Clean up orphaned survey files weekly on Sunday at 3:00 AM
0 3 * * 0 cd /path/to/django_survey_app && /path/to/venv/bin/python manage.py cleanup_orphaned_files >> /var/log/django/cleanup_files.log 2>&1
```

### 3. Important Path Updates

**Replace the following paths with your actual paths:**

- `/path/to/django_survey_app` - Your Django project root directory
- `/path/to/venv/bin/python` - Your Python virtual environment (or use `python3` if not using venv)
- `/var/log/django/` - Your preferred log directory

### 4. Create Log Directory

Create the log directory if it doesn't exist:

```bash
sudo mkdir -p /var/log/django
sudo chown your-django-user:your-django-group /var/log/django
```

## Cron Schedule Explanation

### Cleanup Expired Drafts (Daily)
```
0 2 * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0 and 7 are Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Runs:** Every day at 2:00 AM

### Cleanup Orphaned Files (Weekly)
```
0 3 * * 0
```

**Runs:** Every Sunday at 3:00 AM

## Alternative Schedules

You can adjust the schedule based on your needs:

### Hourly Cleanup
```cron
0 * * * * cd /path/to/project && python manage.py cleanup_expired_drafts
```

### Every 6 Hours
```cron
0 */6 * * * cd /path/to/project && python manage.py cleanup_expired_drafts
```

### Monthly File Cleanup
```cron
0 3 1 * * cd /path/to/project && python manage.py cleanup_orphaned_files
```

## Testing Cron Jobs

### Test Command Execution

Before adding to cron, test the commands manually:

```bash
cd /path/to/django_survey_app
source venv/bin/activate  # If using virtual environment
python manage.py cleanup_expired_drafts
python manage.py cleanup_orphaned_files --dry-run
```

### Verify Cron Installation

Check that your cron jobs are installed:

```bash
crontab -l
```

### Monitor Logs

After setting up cron, monitor the log files:

```bash
tail -f /var/log/django/cleanup_drafts.log
tail -f /var/log/django/cleanup_files.log
```

## Using systemd Timers (Alternative)

If you prefer systemd timers instead of cron:

### 1. Create Service Files

**/etc/systemd/system/django-cleanup-drafts.service**
```ini
[Unit]
Description=Django Survey - Cleanup Expired Drafts
After=network.target

[Service]
Type=oneshot
User=django-user
WorkingDirectory=/path/to/django_survey_app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python manage.py cleanup_expired_drafts
```

**/etc/systemd/system/django-cleanup-drafts.timer**
```ini
[Unit]
Description=Run Django draft cleanup daily
Requires=django-cleanup-drafts.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 2. Enable and Start Timers

```bash
sudo systemctl daemon-reload
sudo systemctl enable django-cleanup-drafts.timer
sudo systemctl start django-cleanup-drafts.timer
sudo systemctl status django-cleanup-drafts.timer
```

## Monitoring and Alerts

### Log Rotation

Add log rotation to prevent log files from growing too large:

**/etc/logrotate.d/django-survey**
```
/var/log/django/cleanup_*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

### Email Notifications

To receive email notifications on failures, set `MAILTO` in crontab:

```cron
MAILTO=admin@example.com

0 2 * * * cd /path/to/project && python manage.py cleanup_expired_drafts
```

### Health Check Integration

Consider adding health check endpoints:

```bash
# After cron runs, ping a monitoring service
0 2 * * * cd /path/to/project && python manage.py cleanup_expired_drafts && curl -fsS https://hc-ping.com/your-uuid > /dev/null
```

## Troubleshooting

### Cron Job Not Running

1. **Check cron service status:**
   ```bash
   sudo systemctl status cron  # Ubuntu/Debian
   sudo systemctl status crond # CentOS/RHEL
   ```

2. **Check system mail for errors:**
   ```bash
   mail
   ```

3. **Verify permissions:**
   ```bash
   ls -la /path/to/django_survey_app
   ls -la /var/log/django
   ```

### Commands Failing

1. **Test with full path:**
   ```bash
   /usr/bin/env bash -c "cd /path/to/project && /path/to/venv/bin/python manage.py cleanup_expired_drafts"
   ```

2. **Check Django settings:**
   - Ensure `DJANGO_SETTINGS_MODULE` is set
   - Verify database connection
   - Check file permissions

3. **View command output:**
   ```bash
   python manage.py cleanup_expired_drafts --verbosity 2
   ```

## Configuration Options

### Draft Expiry Duration

The draft expiry duration is configured in `settings.py`:

```python
# Number of days before drafts expire (default: 30)
SURVEY_DRAFT_EXPIRY_DAYS = 30
```

### File Upload Location

File upload location is also in `settings.py`:

```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

## Best Practices

1. **Run during low-traffic hours** - Schedule cleanups during off-peak times
2. **Monitor disk space** - Ensure cleanup jobs run successfully to prevent disk space issues
3. **Keep logs** - Maintain logs for troubleshooting
4. **Test before deploying** - Always test cron jobs in staging first
5. **Set up alerts** - Configure notifications for job failures
6. **Document changes** - Keep this file updated with any schedule changes

## Security Considerations

- Run cron jobs with minimal privileges
- Ensure log files have appropriate permissions (640 or 600)
- Don't expose sensitive data in logs
- Rotate logs regularly
- Monitor for unusual deletion patterns

## Support

If you encounter issues with the cleanup commands, check:

1. Django logs: `/path/to/logs/django.log`
2. Cron logs: `/var/log/cron` or `/var/log/syslog`
3. Application logs: `/var/log/django/`

For manual cleanup, you can always run commands directly:

```bash
python manage.py cleanup_expired_drafts
python manage.py cleanup_orphaned_files --dry-run
python manage.py cleanup_orphaned_files  # Actually delete
```
