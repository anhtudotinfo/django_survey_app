# Hướng Dẫn Deployment Trên Replit - Django Survey System

## Triển Khai Tự Động

### Bước 1: Khởi động ứng dụng

Khi deploy lần đầu tiên trên Replit, hệ thống sẽ tự động:
- ✅ Chạy database migrations
- ✅ Thu thập static files
- ✅ Khởi động Gunicorn server trên port 5000

### Bước 2: Thiết lập dữ liệu ban đầu

Sau khi ứng dụng đã chạy, mở **Shell** và chạy lệnh sau:

```bash
python manage.py setup_initial_data
```

**Kết quả:**
```
======================================================================
  THIẾT LẬP DỮ LIỆU BAN ĐẦU - CÔNG AN PHƯỜNG AN KHÊ
======================================================================

📌 Bước 1/3: Tạo tài khoản admin...
✅ Successfully created admin user
   Username: admin
   Email: admin@ankhe.police.vn
   Password: Vbpo@12345

📌 Bước 2/3: Tạo mẫu khảo sát GPLX mô tô...
✅ Successfully created GPLX survey
   Survey ID: 1
   Survey slug: khai-bao-gplx-mo-to
   URL: /surveys/khai-bao-gplx-mo-to/
   Sections created: 7
   Total questions: 31

📌 Bước 3/3: Tạo mẫu khảo sát Phương tiện...
✅ Successfully created Vehicle survey
   Survey ID: 2
   Survey slug: khai-bao-phuong-tien
   URL: /surveys/khai-bao-phuong-tien/
   Sections created: 7
   Total questions: 39

======================================================================
✅ HOÀN THÀNH THIẾT LẬP DỮ LIỆU BAN ĐẦU
======================================================================
```

---

## Truy Cập Hệ Thống

### Admin Panel
```
URL: https://your-repl-name.replit.app/admin/
Username: admin
Password: Vbpo@12345
```

### Khảo sát GPLX (31 câu hỏi)
```
URL: https://your-repl-name.replit.app/surveys/khai-bao-gplx-mo-to/
QR Code: https://your-repl-name.replit.app/qr/khai-bao-gplx-mo-to/
```

### Khảo sát Phương tiện (39 câu hỏi)
```
URL: https://your-repl-name.replit.app/surveys/khai-bao-phuong-tien/
QR Code: https://your-repl-name.replit.app/qr/khai-bao-phuong-tien/
```

---

## Bảo Mật (Quan Trọng!)

⚠️ **Ngay sau khi đăng nhập lần đầu:**

1. **Đổi mật khẩu admin:**
   - Đăng nhập /admin/
   - Click vào tên user (góc trên phải)
   - Change password

2. **Kiểm tra cấu hình:**
   - Đảm bảo `DEBUG=False` trong Secrets
   - Kiểm tra `ALLOWED_HOSTS` có domain Replit

3. **Backup dữ liệu:**
   - Download database định kỳ
   - Export CSV responses thường xuyên

---

## Các Lệnh Setup Chi Tiết

### 1. Thiết lập đầy đủ (Recommended)
```bash
python manage.py setup_initial_data
```
Chạy tất cả các lệnh setup: admin + 2 surveys

### 2. Tạo lại surveys (nếu cần)
```bash
python manage.py setup_initial_data --force
```
Xóa và tạo lại các mẫu khảo sát (không ảnh hưởng đến responses)

### 3. Các lệnh riêng lẻ

**Chỉ tạo admin:**
```bash
python manage.py create_admin
```

**Chỉ tạo mẫu GPLX:**
```bash
python manage.py create_gplx_survey
python manage.py create_gplx_survey --force  # Tạo lại
```

**Chỉ tạo mẫu Phương tiện:**
```bash
python manage.py create_vehicle_survey
python manage.py create_vehicle_survey --force  # Tạo lại
```

---

## Thông Tin Mẫu Khảo Sát

### Mẫu 1: KHAI BÁO GIẤY PHÉP LÁI XE MÔ TÔ

**Đặc điểm:**
- 🎯 Mục đích: Làm sạch & đồng bộ dữ liệu GPLX với CSDL dân cư
- 📋 Cấu trúc: 7 sections, 31 questions
- 👥 Người dùng: Công dân cư trú tại phường An Khê
- ⏱ Thời gian: 01/11 - 15/12/2025

**Sections:**
1. **Phần 1 - Hướng dẫn:** Thông tin chung
2. **Phần 2 - Thông tin người khai:** 8 câu (Họ tên, CCCD, ...)
3. **Phần 3 - Chọn số GPLX:** Branching question (1-3 GPLX)
4. **Phần 4 - GPLX 1:** 7 câu (Số GPLX, hạng, ngày cấp, ảnh...)
5. **Phần 5 - GPLX 2:** 7 câu (tương tự GPLX 1)
6. **Phần 6 - GPLX 3:** 7 câu (tương tự GPLX 1)
7. **Phần 7 - Cam kết:** Xác nhận thông tin

**Branching Logic:**
```
Chọn 1 GPLX → Section 4 → Section 7 (Bỏ qua 5, 6)
Chọn 2 GPLX → Section 4 → Section 5 → Section 7 (Bỏ qua 6)
Chọn 3 GPLX → Section 4 → Section 5 → Section 6 → Section 7
```

**Validation:**
- CCCD: 9 hoặc 12 số (`^[0-9]{9}$|^[0-9]{12}$`)
- Điện thoại: 10 số (`^[0-9]{10}$`)
- File upload: .jpg/.png, max 5MB

---

### Mẫu 2: KHAI BÁO THÔNG TIN PHƯƠNG TIỆN

**Đặc điểm:**
- 🎯 Mục đích: Làm sạch dữ liệu đăng ký xe theo kế hoạch CATP
- 📋 Cấu trúc: 7 sections, 39 questions
- 👥 Người dùng: Công dân cư trú tại phường An Khê
- ⏱ Thời gian: 01/11 - 30/11/2025

**Sections:**
1. **Phần 1 - Hướng dẫn:** Thông tin chung
2. **Phần 2 - Thông tin chủ xe:** 10 câu (Họ tên, CCCD, tình trạng cư trú...)
3. **Phần 3 - Chọn số xe:** Branching question (1-3 xe)
4. **Phần 4 - Xe 1:** 9 câu (Biển số, loại xe, nhãn hiệu, ảnh...)
5. **Phần 5 - Xe 2:** 9 câu (tương tự Xe 1)
6. **Phần 6 - Xe 3:** 9 câu (tương tự Xe 1)
7. **Phần 7 - Cam kết:** Xác nhận thông tin

**Branching Logic:**
```
Chọn 1 xe → Section 4 → Section 7 (Bỏ qua 5, 6)
Chọn 2 xe → Section 4 → Section 5 → Section 7 (Bỏ qua 6)
Chọn 3 xe → Section 4 → Section 5 → Section 6 → Section 7
```

**Validation:**
- Tương tự mẫu GPLX
- Thêm: Năm sản xuất (number field)

---

## Quản Lý QR Code

**Cách truy cập QR codes:**

1. **Từ trang chủ:**
   - Vào https://your-repl.replit.app/
   - Xem danh sách surveys
   - Click "QR Code" để xem/in

2. **Trực tiếp:**
   - GPLX: `/qr/khai-bao-gplx-mo-to/`
   - Phương tiện: `/qr/khai-bao-phuong-tien/`

3. **Tính năng QR:**
   - Tự động sinh QR code
   - In trực tiếp từ browser
   - Tải về file PNG
   - Hiển thị full domain

**Sử dụng:**
- In QR code và dán ở bảng tin phường/tổ
- Chia sẻ link cho công dân
- Gửi qua Zalo/Facebook nhóm tổ dân phố

---

## Export Dữ Liệu

**Từ Admin Panel:**

1. Đăng nhập /admin/
2. Vào "Surveys" → Chọn survey cần export
3. Click "View responses"
4. Click "Export CSV"
5. Chọn filter nếu cần:
   - Theo tổ dân phố
   - Theo ngày khai báo
   - Theo tình trạng GPLX/xe

**CSV Format:**
- Tất cả câu trả lời trong một file
- Include device info (IP, browser, OS)
- Include timestamps
- Hỗ trợ tiếng Việt (UTF-8)

---

## Troubleshooting

### 1. Lỗi: Survey đã tồn tại
```bash
# Giải pháp: Dùng --force để tạo lại
python manage.py create_gplx_survey --force
```

### 2. Admin đã tồn tại
```bash
# Không vấn đề gì, lệnh sẽ tự động bỏ qua
# Output: "⚠️  Admin user 'admin' already exists - skipping creation"
```

### 3. Cần xóa tất cả và làm lại
```bash
# ⚠️ CẢNH BÁO: Lệnh này xóa toàn bộ database!
rm db.sqlite3
python manage.py migrate
python manage.py setup_initial_data
```

### 4. Upload file không hoạt động
```bash
# Kiểm tra thư mục media
ls -la media/

# Tạo lại nếu cần
mkdir -p media/survey_*/
chmod 755 media/
```

### 5. Static files không load
```bash
# Collect lại static files
python manage.py collectstatic --noinput --clear

# Restart workflow
# Dùng "Restart" button trong Replit UI
```

---

## Monitoring & Maintenance

### Kiểm tra logs định kỳ

**Workflow logs:**
- Xem trong Replit Console
- Kiểm tra errors
- Monitor traffic

**Database size:**
```bash
# Kiểm tra kích thước database
ls -lh db.sqlite3

# Nếu quá lớn, export & clear old data
```

### Backup thường xuyên

**Export CSV responses:**
- Vào admin → Export CSV
- Lưu file CSV
- Upload lên Google Drive/Dropbox

**Backup database:**
```bash
# Copy db.sqlite3 về máy
# Hoặc sử dụng Replit Download feature
```

---

## Performance Tips

### 1. Giới hạn file uploads
- Max 5MB per file (đã cấu hình)
- Chỉ cho phép .jpg/.png
- Tự động optimize images

### 2. Pagination responses
- Admin tự động phân trang (50 items/page)
- Search & filter để tìm nhanh

### 3. Cache QR codes
- QR codes được cache
- Không cần generate lại mỗi lần

---

## Support & Contact

**Công An Phường An Khê**
- Quận Thanh Khê, TP. Đà Nẵng
- Thời gian hỗ trợ: Giờ hành chính

**Technical Support:**
- Check logs trong Replit Console
- Review Admin Panel errors
- Xem Browser Console (F12) nếu có lỗi UI

---

## Production Checklist

- [ ] Chạy `python manage.py setup_initial_data`
- [ ] Đăng nhập admin thành công
- [ ] Đổi mật khẩu admin
- [ ] Test cả 2 surveys
- [ ] Upload thử file ảnh
- [ ] Kiểm tra QR codes
- [ ] Export CSV thử nghiệm
- [ ] In QR code để phát cho công dân
- [ ] Thông báo thời gian khai báo (01/11-15/12)
- [ ] Setup backup schedule

---

**🎉 Deployment Complete!**

Hệ thống đã sẵn sàng phục vụ công tác khai báo GPLX và phương tiện tại phường An Khê!

**Đã tạo:**
- ✅ Admin account (admin/Vbpo@12345)
- ✅ Mẫu GPLX mô tô (31 câu hỏi, 7 sections)
- ✅ Mẫu Phương tiện (39 câu hỏi, 7 sections)
- ✅ QR codes cho cả 2 mẫu
- ✅ Export CSV functionality
- ✅ Mobile-friendly interface

**Để sử dụng ngay lập tức:**
1. Mở /admin/ → Đổi password
2. In QR codes từ trang chủ
3. Thông báo link cho công dân
4. Bắt đầu thu thập dữ liệu!

**Chúc công tác thuận lợi! 🚀**
