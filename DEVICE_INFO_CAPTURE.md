# Device Information Capture Feature

## Overview
Tính năng thu thập thông tin thiết bị và địa chỉ IP khi người dùng tham gia khảo sát để đảm bảo bảo mật.

## Thông Tin Thu Thập

### 1. IP Address (Địa chỉ IP)
- IPv4 hoặc IPv6
- Xử lý cả direct connection và proxy/load balancer
- Lấy từ `HTTP_X_FORWARDED_FOR` hoặc `REMOTE_ADDR`

### 2. Browser (Trình duyệt)
- Tên và phiên bản
- Ví dụ: "Chrome 120", "Firefox 119", "Microsoft Edge 120"
- Hỗ trợ: Chrome, Firefox, Safari, Edge, Opera

### 3. Operating System (Hệ điều hành)
- Tên và phiên bản
- Ví dụ: "Windows 10/11", "macOS 14.1", "Android 13", "iOS 17.1"
- Hỗ trợ: Windows, macOS, Linux, Android, iOS, Ubuntu

### 4. Device Type (Loại thiết bị)
- Desktop, Mobile, hoặc Tablet
- Tự động phát hiện dựa trên user agent

### 5. User Agent String
- Chuỗi user agent đầy đủ
- Lưu trữ để phân tích sau

## Database Schema

### UserAnswer Model
```python
class UserAnswer(BaseModel):
    # Existing fields
    survey = ForeignKey(Survey)
    user = ForeignKey(User)
    direction = ForeignKey(Direction)
    
    # NEW: Device and security information
    ip_address = GenericIPAddressField(null=True, blank=True)
    user_agent = TextField(blank=True, null=True)
    browser = CharField(max_length=100, blank=True, null=True)
    os = CharField(max_length=100, blank=True, null=True)
    device = CharField(max_length=100, blank=True, null=True)
```

## Implementation

### 1. Utils Functions (`djf_surveys/utils.py`)

#### get_client_ip(request)
```python
def get_client_ip(request):
    """Extract IP from request, handling proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

#### parse_user_agent(user_agent_string)
```python
def parse_user_agent(user_agent_string):
    """Parse user agent to extract browser, OS, device"""
    # Returns: {'browser': '...', 'os': '...', 'device': '...'}
```

#### capture_device_info(request)
```python
def capture_device_info(request):
    """Capture complete device info from request"""
    return {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'browser': '...',
        'os': '...',
        'device': '...'
    }
```

### 2. View Updates (`djf_surveys/views.py`)

#### CreateSurveyFormView._save_current_section_answers()
```python
# Capture device info
device_info = capture_device_info(self.request)

# Create UserAnswer with device info
user_answer = UserAnswer.objects.create(
    survey=survey,
    user=self.request.user,
    direction=None,
    **device_info  # Unpack device info
)
```

Áp dụng cho tất cả các chỗ tạo UserAnswer:
- Authenticated users
- Anonymous users
- Duplicate entry surveys
- Non-duplicate surveys

### 3. CSV Export Updates (`djf_surveys/admins/views.py`)

#### DownloadResponseSurveyView
```python
# Header
header = ['user', 'submitted time', 'IP address', 'browser', 'OS', 'device', ...]

# Rows
rows.append(user_answer.ip_address or 'N/A')
rows.append(user_answer.browser or 'N/A')
rows.append(user_answer.os or 'N/A')
rows.append(user_answer.device or 'N/A')
```

#### DownloadFilteredResponseSurveyView
Same updates for filtered downloads.

### 4. Admin Display Updates (`djf_surveys/admin.py`)

```python
class AdminUserAnswer(admin.ModelAdmin):
    list_display = ('survey', 'user', 'ip_address', 'browser', 'device', 'created_at', 'updated_at')
    list_filter = ('survey', 'browser', 'device', 'created_at')
    search_fields = ('user__username', 'ip_address', 'browser')
    readonly_fields = ('ip_address', 'user_agent', 'browser', 'os', 'device')
```

## CSV Export Format

### Example Output:
```csv
user,submitted time,IP address,browser,OS,device,Question1,Question2,...
admin,2025-11-02 10:30:00,192.168.1.100,Chrome 120,Windows 10/11,Desktop,Answer1,Answer2,...
guest,2025-11-02 10:35:00,192.168.1.101,Safari 17,iOS 17.1,Mobile,Answer1,Answer2,...
```

## Browser Detection Examples

| User Agent | Detected Browser | Detected OS | Device Type |
|------------|-----------------|-------------|-------------|
| Chrome on Windows | Chrome 120 | Windows 10/11 | Desktop |
| Firefox on macOS | Firefox 119 | macOS 14.1 | Desktop |
| Safari on iPhone | Safari 17 | iOS 17.1 | Mobile |
| Chrome on Android | Chrome 120 | Android 13 | Mobile/Tablet |
| Edge on Windows | Microsoft Edge 120 | Windows 10/11 | Desktop |

## Security & Privacy

### Data Collection Purpose
- **Security:** Phát hiện truy cập bất thường
- **Analytics:** Hiểu thiết bị người dùng sử dụng
- **Audit:** Theo dõi nguồn gốc phản hồi

### Privacy Considerations
- ✅ IP addresses có thể là thông tin nhận dạng cá nhân
- ✅ Chỉ staff/admin có quyền xem
- ✅ Không hiển thị cho người dùng thường
- ✅ Tuân thủ GDPR/privacy laws nếu áp dụng

### GDPR Compliance
Nếu cần tuân thủ GDPR:
1. Thông báo người dùng về việc thu thập dữ liệu
2. Cho phép từ chối (opt-out)
3. Cho phép xóa dữ liệu theo yêu cầu
4. Giới hạn thời gian lưu trữ

## Usage Examples

### 1. View in Admin
```
/admin/djf_surveys/useranswer/
- Click vào bất kỳ UserAnswer
- Xem thông tin: IP, Browser, OS, Device
```

### 2. Download CSV
```
/dashboard/download/survey/{slug}/
- CSV includes device info columns
- Use for analysis in Excel/Google Sheets
```

### 3. Filter by Device
```
/admin/djf_surveys/useranswer/?device=Mobile
- See all mobile responses
- Filter by browser, device type
```

### 4. Search by IP
```
/admin/djf_surveys/useranswer/?q=192.168.1.100
- Find all responses from specific IP
- Security investigation
```

## Testing

### Manual Test:
1. Submit survey from different devices:
   - Desktop (Chrome, Firefox)
   - Mobile (Safari, Chrome)
   - Tablet (iPad Safari)

2. Check admin panel:
   ```
   /admin/djf_surveys/useranswer/
   ```
   Verify each field is populated correctly

3. Download CSV:
   ```
   /dashboard/download/survey/{slug}/
   ```
   Verify device columns present

### Automated Test:
```python
from djf_surveys.utils import parse_user_agent

# Test Chrome on Windows
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
result = parse_user_agent(ua)
assert result['browser'] == 'Chrome 120'
assert result['os'] == 'Windows 10/11'
assert result['device'] == 'Desktop'

# Test Safari on iPhone
ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
result = parse_user_agent(ua)
assert result['browser'] == 'Safari 17'
assert result['os'] == 'iOS 17.1'
assert result['device'] == 'Mobile'
```

## Maintenance

### Adding New Browser Support:
Edit `parse_user_agent()` in `utils.py`:
```python
elif 'newbrowser/' in ua:
    browser = 'NewBrowser'
    version_match = re.search(r'newbrowser/(\d+)', ua)
    if version_match:
        browser += f' {version_match.group(1)}'
```

### Adding New OS Support:
```python
elif 'newos' in ua:
    os_name = 'NewOS'
    # Extract version if needed
```

## Troubleshooting

### IP shows as 127.0.0.1
- Running locally? Normal for localhost
- Behind proxy? Check `HTTP_X_FORWARDED_FOR` configuration

### Browser shows as "Unknown"
- User agent not recognized
- Check user agent string in database
- Add detection logic if needed

### Device info not captured
- Check migration applied: `python manage.py migrate`
- Check view imports `capture_device_info`
- Check `**device_info` passed to create()

## Files Modified

1. **djf_surveys/models.py** - Added fields to UserAnswer
2. **djf_surveys/migrations/0029_*.py** - Migration file
3. **djf_surveys/utils.py** - Device detection functions
4. **djf_surveys/views.py** - Capture device info on submission
5. **djf_surveys/admins/views.py** - Include in CSV exports
6. **djf_surveys/admin.py** - Display in admin panel

## Benefits

✅ **Security:** Track suspicious activity  
✅ **Analytics:** Understand user devices  
✅ **Support:** Help debug device-specific issues  
✅ **Compliance:** Audit trail for responses  
✅ **Insights:** Device/browser usage statistics  

## Future Enhancements

- [ ] Geolocation dari IP
- [ ] Device fingerprinting
- [ ] Fraud detection
- [ ] Real-time alerts for suspicious IPs
- [ ] Dashboard with device statistics
- [ ] IP blacklist/whitelist

---

**Status:** ✅ FULLY IMPLEMENTED  
**Date:** 2025-11-02  
**Version:** 1.0
