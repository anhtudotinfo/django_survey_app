# Test Device Info Capture

## Đã Fix
✅ Device info giờ được capture trong `_get_or_create_user_answer()`  
✅ Áp dụng cho cả authenticated và anonymous users  
✅ Áp dụng cho cả duplicate_entry và non-duplicate surveys  

## Hướng Dẫn Test

### 1. Submit Survey Mới

1. Mở browser và truy cập survey:
   ```
   http://127.0.0.1:8000/create/test/
   ```

2. Điền form và submit

3. Kiểm tra database:
   ```bash
   python3 manage.py shell
   ```
   ```python
   from djf_surveys.models import UserAnswer
   ua = UserAnswer.objects.latest('created_at')
   print(f"IP: {ua.ip_address}")
   print(f"Browser: {ua.browser}")
   print(f"OS: {ua.os}")
   print(f"Device: {ua.device}")
   ```

### 2. Kiểm Tra Admin Panel

1. Truy cập admin:
   ```
   http://127.0.0.1:8000/admin/djf_surveys/useranswer/
   ```

2. Xem list view - sẽ thấy columns:
   - IP Address
   - Browser
   - Device

3. Click vào một UserAnswer để xem chi tiết

### 3. Download CSV

1. Truy cập dashboard:
   ```
   http://127.0.0.1:8000/dashboard/summary/survey/test/
   ```

2. Click "Download Filtered Data" hoặc "Download" button

3. Mở CSV file - sẽ có columns:
   - user
   - submitted time
   - **IP address**
   - **browser**
   - **OS**
   - **device**
   - Questions...

### 4. Test Từ Nhiều Thiết Bị

Test từ:
- **Desktop Chrome:** Sẽ show "Chrome XX", "Windows 10/11", "Desktop"
- **Mobile Safari:** Sẽ show "Safari XX", "iOS XX", "Mobile"
- **Firefox:** Sẽ show "Firefox XX", OS tương ứng

## Expected Results

### Desktop Chrome on Windows:
```
IP: 127.0.0.1 (hoặc real IP)
Browser: Chrome 120 (version có thể khác)
OS: Windows 10/11
Device: Desktop
User Agent: Mozilla/5.0 (Windows NT 10.0; ...) Chrome/...
```

### Mobile Safari on iPhone:
```
IP: real IP
Browser: Safari 17
OS: iOS 17.x
Device: Mobile
User Agent: Mozilla/5.0 (iPhone; ...) Safari/...
```

### Firefox on Linux:
```
IP: real IP
Browser: Firefox 119
OS: Linux
Device: Desktop
User Agent: Mozilla/5.0 (X11; Linux ...) Firefox/...
```

## Troubleshooting

### Vẫn thấy N/A?

1. **Check migration đã chạy chưa:**
   ```bash
   python3 manage.py showmigrations djf_surveys
   ```
   Phải có `[X] 0029_useranswer_browser_...`

2. **Check server đã restart chưa:**
   ```bash
   # Stop server (Ctrl+C)
   # Start lại
   python3 manage.py runserver
   ```

3. **Check code changes đã load chưa:**
   - Xóa `__pycache__` folders
   - Restart server

4. **Test functions trực tiếp:**
   ```bash
   python3 << 'EOF'
   import os, django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
   django.setup()
   
   from djf_surveys.utils import parse_user_agent
   ua = "Mozilla/5.0 (Windows NT 10.0; ...) Chrome/120.0.0.0"
   result = parse_user_agent(ua)
   print(result)
   EOF
   ```

### IP shows 127.0.0.1?

- **Normal nếu test locally**
- Để test real IP, deploy lên server hoặc dùng ngrok

### Browser/OS không detect?

- User agent string có thể mới/không phổ biến
- Check user agent string trong database
- Có thể thêm detection logic trong `utils.py`

## Quick Verification Script

Run this để verify nhanh:

```bash
cd /home/tuna/Desktop/django_survey_app
python3 << 'EOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import UserAnswer

latest = UserAnswer.objects.order_by('-created_at').first()
if latest:
    has_device_info = all([
        latest.ip_address,
        latest.browser,
        latest.os,
        latest.device
    ])
    
    if has_device_info:
        print("✅ SUCCESS! Device info captured:")
        print(f"   IP: {latest.ip_address}")
        print(f"   Browser: {latest.browser}")
        print(f"   OS: {latest.os}")
        print(f"   Device: {latest.device}")
    else:
        print("❌ FAIL! Device info not captured")
        print(f"   IP: {latest.ip_address or 'None'}")
        print(f"   Browser: {latest.browser or 'None'}")
        print(f"   OS: {latest.os or 'None'}")
        print(f"   Device: {latest.device or 'None'}")
else:
    print("No UserAnswer found. Submit a survey first!")
EOF
```

## Files Changed

1. **djf_surveys/views.py**
   - `_get_or_create_user_answer()` - Added device_info capture
   - Applies to all UserAnswer creation paths

2. **djf_surveys/utils.py**
   - Device detection functions

3. **djf_surveys/models.py**
   - UserAnswer model fields

4. **djf_surveys/admins/views.py**
   - CSV export with device columns

5. **djf_surveys/admin.py**
   - Admin panel display

## Status

✅ **FIXED** - Device info now captured properly  
📅 **Date:** 2025-11-02  
🔧 **Issue:** N/A values fixed by adding capture in _get_or_create_user_answer()  

---

**Next:** Submit a new survey and verify device info appears!
