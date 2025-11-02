# Quick Guide: Device Info Capture

## Tóm Tắt
Thu thập thông tin thiết bị và IP khi khảo sát để đảm bảo bảo mật.

## Thông Tin Thu Thập
1. **IP Address** - Địa chỉ IP thiết bị
2. **Browser** - Trình duyệt (Chrome, Firefox, Safari, v.v.)
3. **OS** - Hệ điều hành (Windows, macOS, Android, iOS)
4. **Device** - Loại thiết bị (Desktop, Mobile, Tablet)
5. **User Agent** - Chuỗi user agent đầy đủ

## Xem Thông Tin

### 1. Trong Admin Panel
```
/admin/djf_surveys/useranswer/
```
- List view shows: Survey, User, IP, Browser, Device, Time
- Click vào record để xem chi tiết

### 2. Trong CSV Export
```
/dashboard/download/survey/{slug}/
```
CSV columns: User, Time, **IP Address, Browser, OS, Device**, Questions...

### 3. Filter và Search
- Filter by Browser: Chrome, Firefox, Safari, etc.
- Filter by Device: Desktop, Mobile, Tablet
- Search by IP: Tìm responses từ IP cụ thể

## Ví Dụ Dữ Liệu

| User | IP | Browser | OS | Device |
|------|----|---------|----|--------|
| admin | 192.168.1.100 | Chrome 120 | Windows 10/11 | Desktop |
| guest | 192.168.1.101 | Safari 17 | iOS 17.1 | Mobile |
| user1 | 192.168.1.102 | Firefox 119 | macOS 14.1 | Desktop |

## Use Cases

### 1. Bảo Mật
- Phát hiện truy cập bất thường
- Track multiple submissions từ cùng IP
- Identify bot traffic

### 2. Analytics  
- Hiểu thiết bị người dùng sử dụng
- Tối ưu hóa cho mobile/desktop
- Browser compatibility insights

### 3. Support
- Debug device-specific issues
- Reproduce user problems
- Better user assistance

## Lưu Ý Bảo Mật

⚠️ **Privacy:**
- IP addresses có thể nhận dạng người dùng
- Chỉ staff/admin xem được
- Tuân thủ privacy laws (GDPR nếu áp dụng)

✅ **Best Practices:**
- Thông báo người dùng về thu thập dữ liệu
- Giới hạn quyền truy cập
- Xóa dữ liệu cũ định kỳ nếu cần

## Automatic Capture

Device info được capture **tự động** khi:
- User submit survey
- Mỗi section trong multi-section survey
- Cả authenticated và anonymous users

Không cần cấu hình thêm!

---

**Date:** 2025-11-02  
**Status:** ✅ Active  
**Documentation:** See DEVICE_INFO_CAPTURE.md for full details
