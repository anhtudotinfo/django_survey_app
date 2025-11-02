# Hướng Dẫn Tạo và Sử Dụng Mã QR

## ✅ Đã Cập Nhật

Trang chủ giờ đã hiển thị:
- **Domain + URL đầy đủ** của hệ thống
- Hộp highlight với địa chỉ truy cập
- Hướng dẫn sao chép và tạo QR code

## 📱 Xem Ngay

```bash
python3 manage.py runserver
# Truy cập: http://127.0.0.1:8000/
```

Bạn sẽ thấy địa chỉ hiển thị ở phần "Quét Mã QR - Khai Báo Nhanh"

## 🎯 Cách Tạo Mã QR

### Cách 1: Tạo QR Cho Trang Chủ (Recommend)

1. **Lấy URL từ trang chủ**
   - URL hiển thị: `http://yourdomain.com` hoặc `http://127.0.0.1:8000`
   
2. **Tạo QR Code trực tuyến** (MIỄN PHÍ)
   - Vào: https://qr-code-generator.com
   - Dán URL vào ô "Website URL"
   - Click "Create QR Code"
   - Download PNG hoặc PDF

3. **Hoặc dùng công cụ khác:**
   - https://www.qrcode-monkey.com (Có logo custom)
   - https://www.the-qrcode-generator.com
   - https://goqr.me

### Cách 2: Tạo QR Cho Từng Biểu Mẫu

1. **Lấy URL biểu mẫu cụ thể**
   - Ví dụ: `http://yourdomain.com/create/khao-sat-an-ninh/`
   
2. **Tạo QR như trên**

3. **Lợi ích:**
   - Người dân quét trực tiếp vào biểu mẫu
   - Không cần chọn trong danh sách

### Cách 3: Tạo QR Tự Động Trong Admin

Nếu bạn muốn tự động, có thể:

1. **Install qrcode package:**
```bash
pip install qrcode[pil]
```

2. **Tạo view để generate QR:**
```python
# views.py
import qrcode
from io import BytesIO
from django.http import HttpResponse

def generate_qr(request, slug):
    survey_url = request.build_absolute_uri(
        reverse('djf_surveys:create_survey', args=[slug])
    )
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(survey_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Return as image
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type='image/png')
```

## 📋 Kích Thước In Đề Xuất

### 1. Poster A4 (Dán tại UBND, Công An)
- **Kích thước QR:** 10cm x 10cm
- **Độ phân giải:** 300 DPI
- **Format:** PNG hoặc PDF

**Template:**
```
┌─────────────────────────────┐
│   [Logo Công An]            │
│                             │
│  KHAI BÁO THÔNG TIN         │
│  PHƯỜNG AN KHÊ              │
│                             │
│    [QR CODE 10x10cm]        │
│                             │
│  Quét mã QR để khai báo     │
│  http://your-url.com        │
└─────────────────────────────┘
```

### 2. Tờ Rơi A5
- **Kích thước QR:** 5cm x 5cm
- **In 2 mặt:** Mặt 1: QR, Mặt 2: Hướng dẫn

### 3. Sticker Nhỏ
- **Kích thước:** 3cm x 3cm
- **Dán:** Tại tổ dân phố, khu vực công cộng

## 🎨 Thiết Kế Poster Chuyên Nghiệp

### Template Word/PowerPoint:

```
╔═══════════════════════════════════════╗
║                                       ║
║    🏛️ CÔNG AN PHƯỜNG AN KHÊ          ║
║       Quận Thanh Khê - TP. Đà Nẵng   ║
║                                       ║
║  ═══════════════════════════════════  ║
║                                       ║
║     KHAI BÁO THÔNG TIN TRỰC TUYẾN    ║
║                                       ║
║            [QR CODE HERE]             ║
║              10cm x 10cm              ║
║                                       ║
║  ─────────────────────────────────── ║
║                                       ║
║  ✓ Quét mã QR bằng điện thoại        ║
║  ✓ Khai báo thông tin nhanh chóng    ║
║  ✓ Không cần cài đặt ứng dụng        ║
║                                       ║
║  🔗 http://your-domain.com           ║
║                                       ║
║  📞 Hotline: 0236.xxx.xxxx           ║
║                                       ║
╚═══════════════════════════════════════╝
```

## 🖨️ In Ấn

### Khuyến Nghị:
- **Giấy:** 200gsm (dày, bền)
- **In màu:** Full color
- **Cán màng:** Bóng (chống nước)
- **Số lượng:**
  - Poster A4: 50-100 tờ
  - Tờ rơi A5: 500-1000 tờ
  - Sticker: 200-500 cái

### Chi Phí Ước Tính:
- Poster A4: ~5,000đ/tờ
- Tờ rơi A5: ~2,000đ/tờ
- Sticker 3x3cm: ~1,000đ/cái

## 📍 Địa Điểm Đặt QR Code

### Ưu Tiên:
1. ✅ Trụ sở Công An Phường
2. ✅ UBND Phường
3. ✅ Bảng tin tại các khu dân cư
4. ✅ Trạm Y tế
5. ✅ Trường học trong phường
6. ✅ Chợ, siêu thị

### Phụ:
- Quán cà phê, nhà hàng
- Cửa hàng tiện lợi
- Điểm sinh hoạt cộng đồng

## 📱 Hướng Dẫn Người Dân

### Cách Quét QR Code:

**Với iPhone (iOS 11+):**
1. Mở Camera
2. Chĩa vào mã QR
3. Nhấn vào thông báo xuất hiện

**Với Android:**
1. Mở Camera hoặc Google Lens
2. Chĩa vào mã QR
3. Nhấn vào link xuất hiện

**Nếu không quét được:**
- Gõ trực tiếp: `http://your-url.com`

## 🎯 Tips Tăng Hiệu Quả

### 1. Tuyên Truyền
- Thông báo qua loa phát thanh
- Đăng lên Group Facebook phường
- Gửi Zalo nhóm tổ dân phố
- Họp dân phố giới thiệu

### 2. Động Viên
- Tặng quà nhỏ cho người tham gia đầu tiên
- Tổ chức rút thăm may mắn
- Công khai kết quả trên bảng tin

### 3. Hỗ Trợ
- Bố trí cán bộ tại địa điểm có QR
- Hỗ trợ người cao tuổi
- Giải đáp thắc mắc

## 📊 Theo Dõi Hiệu Quả

### Metrics:
- Số lượt scan QR (Google Analytics)
- Số người hoàn thành biểu mẫu
- Tỷ lệ hoàn thành
- Thời gian trung bình

### Dashboard Admin:
```
http://your-domain.com/dashboard/summary/survey/slug/
```

## 🔧 Nâng Cao

### Tạo QR Code Động (Advanced)

Nếu muốn theo dõi ai scan QR:

```python
# Add tracking parameter
url = f"http://yourdomain.com?utm_source=qr&utm_campaign=ankhe"

# Generate QR with this URL
# Analytics sẽ track được
```

### Tích Hợp Google Analytics

Trong template, thêm:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

## 📞 Hỗ Trợ Kỹ Thuật

### Nếu gặp vấn đề:

1. **QR không quét được:**
   - Check URL có chính xác không
   - Regenerate QR code
   - Tăng kích thước QR

2. **Link không mở:**
   - Check server có chạy không
   - Check domain có hoạt động không
   - Check firewall settings

3. **Người dân không biết cách:**
   - In hướng dẫn chi tiết
   - Video hướng dẫn ngắn
   - Hỗ trợ trực tiếp

---

**Đơn Vị:** Công An Phường An Khê  
**Ngày:** 2025-11-02  
**Phiên Bản:** 1.0  

✅ **Sẵn sàng triển khai QR Code!**
