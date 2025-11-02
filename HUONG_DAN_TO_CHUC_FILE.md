# Hướng dẫn Tổ chức và Tải xuống File

## Tổng quan
Hệ thống khảo sát giờ đây hỗ trợ 2 chế độ tổ chức file: theo lượt khảo sát hoặc theo câu hỏi. Tất cả file có thể tải xuống dạng ZIP với cấu trúc rõ ràng và metadata đầy đủ.

## 🎯 Hai chế độ tổ chức file

### Chế độ 1: Theo Lượt Khảo Sát (Mặc định)

**Cấu trúc thư mục:**
```
survey_5/
├── response_101/          ← Lượt khảo sát #101
│   ├── Q15_20250102_143025_resume.pdf
│   ├── Q16_20250102_143030_photo.jpg
│   └── Q17_20250102_143035_cover_letter.pdf
├── response_102/          ← Lượt khảo sát #102
│   ├── Q15_20250102_150000_resume.pdf
│   └── Q16_20250102_150015_photo.jpg
└── ...
```

**Khi nào dùng:**
- ✅ Muốn xem toàn bộ file của 1 người nộp
- ✅ File liên quan đến cùng 1 người/thực thể
- ✅ Tải xuống từng lượt khảo sát riêng lẻ
- ✅ Lưu trữ phản hồi hoàn chỉnh

**Định dạng tên file:**
```
Q{id_câu_hỏi}_{thời_gian}_{tên_file_gốc}

Ví dụ:
Q15_20250102_143025_resume.pdf
  │   │            │         └─ Tên file gốc
  │   │            └─────────── Timestamp (năm/tháng/ngày_giờ/phút/giây)
  │   └──────────────────────── ID câu hỏi
  └──────────────────────────── Q = Question
```

### Chế độ 2: Theo Câu Hỏi

**Cấu trúc thư mục:**
```
survey_5/
├── question_15/           ← Câu hỏi #15 (Upload resume)
│   ├── R101_20250102_143025_resume.pdf
│   ├── R102_20250102_150000_resume.pdf
│   └── R103_20250102_160000_resume.pdf
├── question_16/           ← Câu hỏi #16 (Upload photo)
│   ├── R101_20250102_143030_photo.jpg
│   └── R102_20250102_150015_photo.jpg
└── ...
```

**Khi nào dùng:**
- ✅ So sánh câu trả lời của nhiều người cho cùng câu hỏi
- ✅ Xử lý hàng loạt file cùng loại
- ✅ Phân tích mẫu file upload
- ✅ Kiểm tra chất lượng file cho câu hỏi cụ thể

**Định dạng tên file:**
```
R{id_lượt_khảo_sát}_{thời_gian}_{tên_file_gốc}

Ví dụ:
R101_20250102_143025_resume.pdf
  │    │            │         └─ Tên file gốc
  │    │            └─────────── Timestamp
  │    └──────────────────────── ID lượt khảo sát
  └───────────────────────────── R = Response
```

## 📦 Tải xuống folder khảo sát

### Nội dung file ZIP

Khi tải xuống, bạn sẽ nhận được file ZIP chứa:

#### 1. **Tất cả file đã upload** với cấu trúc thư mục đúng
#### 2. **README.txt** - Thông tin tổng quan
```
Survey Files Download
=====================

Survey Name: Khảo sát tuyển dụng
Survey ID: 5
Organization Type: By Response (One folder per submission)
Download Date: 2025-01-02 14:30:25
Total Files: 12

File Organization:
- Files are organized by response/submission
- Each folder represents one user's submission
- Filename format: Q{question_id}_{timestamp}_{original_name}

File Mapping:
----------------------------------------

File: survey_5/response_101/Q15_20250102_143025_resume.pdf
  Question: Vui lòng upload CV
  Response ID: 101
  User: nguyen_van_a
  Uploaded: 2025-01-02 14:30

[...danh sách đầy đủ các file...]

Statistics:
  Total files: 12
  Total size: 15.3 MB
```

#### 3. **file_list.csv** - Danh sách file dạng bảng
```csv
File Path,Question,Response ID,User,Upload Date
"survey_5/response_101/Q15_20250102_143025_resume.pdf","Upload CV",101,"nguyen_van_a","2025-01-02 14:30"
"survey_5/response_101/Q16_20250102_143030_photo.jpg","Upload ảnh",101,"nguyen_van_a","2025-01-02 14:30"
...
```

## 🚀 Cách sử dụng

### Cài đặt chế độ tổ chức file

#### Trong Admin Interface
1. Vào trang **Edit Survey**
2. Tìm phần **"File Organization"**
3. Chọn một trong hai:
   - ⚪ **By Response** - Theo lượt khảo sát (mặc định)
   - ⚪ **By Question** - Theo câu hỏi
4. **Save** survey

#### Lưu ý quan trọng
- ⚠️ Chế độ áp dụng cho file upload **sau khi** thay đổi
- File đã upload trước đó vẫn giữ cấu trúc cũ
- Nên chọn chế độ **trước** khi khảo sát đi vào hoạt động

### Tải xuống tất cả file

#### Cách 1: Qua Admin Interface
1. Vào trang **Summary** của survey
2. Click nút **Download Files** (nút màu xanh dương, icon cloud)
3. File ZIP sẽ tự động tải xuống
4. Tên file: `survey_{tên-khảo-sát}_files_{timestamp}.zip`

#### Cách 2: Qua URL trực tiếp
```
/download/survey-files/{survey-slug}/
```

**Yêu cầu:**
- Phải đăng nhập
- Phải là staff/admin
- Survey phải có file đã upload

### Giải nén và sử dụng

1. **Mở file ZIP** đã tải
2. **Đọc README.txt** để hiểu cấu trúc
3. **Mở file_list.csv** trong Excel để xem danh sách
4. **Truy cập file** theo thư mục

## 📊 Thông tin trong tên file

### Ví dụ: Q15_20250102_143025_resume.pdf

| Phần | Ý nghĩa | Giá trị |
|------|---------|---------|
| Q15 | Câu hỏi số 15 | Question ID |
| 20250102 | Ngày upload | 2025-01-02 |
| 143025 | Giờ upload | 14:30:25 |
| resume.pdf | Tên file gốc | Original name |

### Lợi ích của format này:

1. **Dễ nhận diện**: Biết ngay file thuộc câu hỏi/response nào
2. **Không trùng lặp**: Timestamp đảm bảo unique
3. **Dễ sắp xếp**: Sort theo thời gian
4. **Truy xuất**: Mapping với database dễ dàng
5. **Tên gốc giữ lại**: Nhận biết nội dung file

## 🔍 Xem thống kê file

### Trong Admin Summary
Thông tin hiển thị:
- Tổng số file đã upload
- Dung lượng tổng cộng
- Chế độ tổ chức
- Thư mục gốc

### Qua Code (nếu cần)
```python
from djf_surveys.models import Survey

survey = Survey.objects.get(id=5)
stats = survey.get_file_statistics()

print(f"Số file: {stats['file_count']}")
print(f"Dung lượng: {stats['total_size_mb']} MB")
print(f"Chế độ: {stats['organization_type']}")
```

## 💡 Best Practices

### Chọn chế độ phù hợp

**Chọn "By Response" khi:**
- Khảo sát tuyển dụng (CV, cover letter, portfolio của 1 người)
- Đăng ký sự kiện (ticket, ID, photo của 1 người)
- Hồ sơ xin học (bằng cấp, chứng chỉ của 1 người)
- Cần xem tất cả file của 1 người cùng lúc

**Chọn "By Question" khi:**
- Cuộc thi ảnh (so sánh tất cả ảnh tham gia)
- Thu thập tài liệu cùng loại (tất cả CV để review)
- Xử lý hàng loạt (batch processing)
- Phân tích tập trung theo từng loại file

### Quản lý file hiệu quả

1. **Đặt tên survey rõ ràng** → Tên folder dễ nhận biết
2. **Tải xuống định kỳ** → Backup dữ liệu
3. **Lưu trữ có tổ chức** → Dễ tìm lại sau này
4. **Đọc README** → Hiểu cấu trúc trước khi xử lý
5. **Dùng CSV** → Import vào Excel để phân tích

## 🎓 Ví dụ thực tế

### Ví dụ 1: Khảo sát tuyển dụng

**Setup:**
- Tên: "Tuyển dụng 2025"
- Chế độ: **By Response** ⭐
- Câu hỏi:
  - Q1: Upload CV
  - Q2: Upload cover letter
  - Q3: Upload portfolio

**Kết quả:**
```
survey_12/
├── response_101/          ← Ứng viên Nguyễn Văn A
│   ├── Q1_20250102_100000_nguyen_van_a_cv.pdf
│   ├── Q2_20250102_100015_nguyen_van_a_cover.pdf
│   └── Q3_20250102_100030_nguyen_van_a_portfolio.zip
├── response_102/          ← Ứng viên Trần Thị B
│   ├── Q1_20250102_110000_tran_thi_b_cv.pdf
│   └── Q2_20250102_110015_tran_thi_b_cover.pdf
└── ...
```

**Lợi ích:**
- Mỗi folder = 1 ứng viên hoàn chỉnh
- Dễ review từng hồ sơ
- Dễ forward cho HR

### Ví dụ 2: Cuộc thi ảnh

**Setup:**
- Tên: "Photo Contest 2025"
- Chế độ: **By Question** ⭐
- Câu hỏi:
  - Q1: Upload ảnh dự thi

**Kết quả:**
```
survey_13/
└── question_8/            ← Tất cả ảnh dự thi
    ├── R201_20250102_090000_photo_nguyen_van_a.jpg
    ├── R202_20250102_091500_photo_tran_thi_b.jpg
    ├── R203_20250102_093000_photo_le_van_c.jpg
    └── ...
```

**Lợi ích:**
- Tất cả ảnh trong 1 folder
- Dễ so sánh và chấm điểm
- Dễ tạo gallery/slideshow

### Ví dụ 3: Thu thập tài liệu

**Setup:**
- Tên: "Thu thập giáo án"
- Chế độ: **By Question** ⭐
- Câu hỏi nhiều:
  - Q1: Giáo án Toán
  - Q2: Giáo án Văn
  - Q3: Giáo án Anh

**Kết quả:**
```
survey_14/
├── question_10/           ← Tất cả giáo án Toán
│   ├── R301_20250102_080000_giao_an_toan.docx
│   ├── R302_20250102_090000_giao_an_toan.docx
│   └── ...
├── question_11/           ← Tất cả giáo án Văn
│   ├── R301_20250102_080100_giao_an_van.docx
│   └── ...
└── question_12/           ← Tất cả giáo án Anh
    └── ...
```

**Lợi ích:**
- File cùng môn trong 1 folder
- Dễ tổng hợp theo môn học
- Thuận tiện cho trưởng bộ môn review

## 📥 Hướng dẫn tải xuống

### Bước 1: Truy cập trang Summary
1. Đăng nhập với tài khoản admin
2. Vào danh sách surveys
3. Click vào survey cần tải file

### Bước 2: Tải xuống
1. Trên trang Summary, tìm các nút action ở góc phải
2. Click nút **màu xanh dương** (icon cloud với mũi tên xuống)
3. Chờ hệ thống tạo ZIP (vài giây đến vài phút)
4. File ZIP tự động tải về

### Bước 3: Giải nén và sử dụng
1. Click đúp vào file ZIP để giải nén
2. Đọc **README.txt** để hiểu cấu trúc
3. Mở **file_list.csv** trong Excel
4. Truy cập file theo thư mục

## 📋 Thông tin trong ZIP

### README.txt chứa:
- ✓ Tên và ID survey
- ✓ Chế độ tổ chức file
- ✓ Ngày giờ tải xuống
- ✓ Tổng số file
- ✓ Danh sách chi tiết mỗi file
- ✓ Thông tin người upload
- ✓ Thống kê tổng quan

### file_list.csv cho phép:
- ✓ Mở trong Excel/Google Sheets
- ✓ Filter và sort dữ liệu
- ✓ Pivot table phân tích
- ✓ Export sang các định dạng khác

## 🛠️ Kỹ thuật

### Quy tắc đặt tên file

1. **Prefix** (Q hoặc R):
   - Chế độ "By Response" → Dùng Q (Question)
   - Chế độ "By Question" → Dùng R (Response)

2. **Timestamp**:
   - Format: YYYYMMDD_HHMMSS
   - Ví dụ: 20250102_143025 = 2/1/2025 lúc 14:30:25
   - Đảm bảo không trùng tên
   - Sắp xếp theo thời gian

3. **Tên file gốc**:
   - Được làm sạch (remove ký tự đặc biệt)
   - Giới hạn 50 ký tự
   - Giữ nguyên phần mở rộng (.pdf, .jpg, ...)

### Bảo mật

- ✅ Chỉ staff/admin tải được
- ✅ Kiểm tra quyền truy cập
- ✅ Path được validate
- ✅ Không lộ thông tin nhạy cảm
- ✅ Tuân thủ privacy settings

### Hiệu năng

- ZIP tạo trong memory (không ghi disk)
- Xử lý streaming cho file lớn
- Query tối ưu với select_related
- Cache statistics khi có thể

## ⚠️ Xử lý sự cố

### Không tải được ZIP
**Nguyên nhân:**
- Không phải staff user
- Không có file nào uploaded
- Lỗi server

**Giải pháp:**
1. Kiểm tra quyền admin
2. Xem có file trong survey không
3. Thử lại sau vài phút
4. Liên hệ admin hệ thống

### File bị thiếu trong ZIP
**Nguyên nhân:**
- File đã bị xóa từ server
- Path không đúng
- Quyền truy cập file

**Giải pháp:**
1. Kiểm tra README.txt xem có lỗi không
2. Kiểm tra media folder trên server
3. Xem log Django
4. Liên hệ admin

### ZIP quá lớn không tải được
**Nguyên nhân:**
- Tổng file size quá lớn
- Timeout server

**Giải pháp:**
1. Tải theo từng tháng (filter trước)
2. Yêu cầu admin tăng timeout
3. Tải từng response riêng lẻ (tính năng tương lai)

### Tên file bị lỗi font
**Nguyên nhân:**
- Tên file gốc có ký tự đặc biệt
- Unicode không support

**Giải pháp:**
- Hệ thống tự động làm sạch
- Dùng ID mapping trong README
- Xem file_list.csv

## 🎯 Tips & Tricks

### Cho Admin
1. **Backup định kỳ**: Tải ZIP về backup mỗi tháng
2. **Chọn chế độ sớm**: Trước khi khảo sát bắt đầu
3. **Test trước**: Tải vài file test xem cấu trúc
4. **Dùng CSV**: Phân tích trong Excel
5. **Lưu trữ có hệ thống**: Tạo folder backup theo năm/tháng

### Cho người dùng
1. **Đặt tên file rõ ràng**: Dễ nhận biết sau này
2. **Không dùng ký tự đặc biệt**: Tránh lỗi
3. **Kiểm tra trước upload**: Đúng file chưa
4. **Kích thước hợp lý**: Không quá lớn

## 📈 Use Cases thực tế

### 1. Tuyển dụng
- **Chế độ**: By Response
- **Lợi ích**: Mỗi folder = 1 ứng viên
- **Workflow**: HR review từng folder

### 2. Thu bài tập
- **Chế độ**: By Response  
- **Lợi ích**: Mỗi folder = 1 học sinh
- **Workflow**: Giáo viên chấm từng folder

### 3. Cuộc thi
- **Chế độ**: By Question
- **Lợi ích**: Tất cả tác phẩm trong 1 folder
- **Workflow**: Ban giám khảo xem hết trong 1 chỗ

### 4. Thu thập tài liệu
- **Chế độ**: By Question
- **Lợi ích**: File cùng loại gom lại
- **Workflow**: Xử lý hàng loạt

### 5. Đăng ký sự kiện
- **Chế độ**: By Response
- **Lợi ích**: Hồ sơ từng người đầy đủ
- **Workflow**: Check-in từng người

## 🔧 Technical API

### Survey Model Methods

```python
# Get folder path
survey.get_upload_folder_path()
# → 'survey_5'

# Get all files
files = survey.get_all_uploaded_files()
# → QuerySet of Answer objects

# Get statistics
stats = survey.get_file_statistics()
# → {
#     'file_count': 12,
#     'total_size_mb': 15.3,
#     'organization_type': 'response',
#     'base_folder': 'survey_5'
# }
```

### File Upload Function

```python
upload_survey_file(instance, filename)
# Automatically:
# 1. Gets survey organization mode
# 2. Cleans filename
# 3. Generates timestamp
# 4. Creates proper path
# 5. Returns path string
```

## 📝 Checklist triển khai

### Trước khi khảo sát đi vào hoạt động:

- [ ] Chọn chế độ tổ chức file phù hợp
- [ ] Test upload 1-2 file thử
- [ ] Kiểm tra cấu trúc folder
- [ ] Verify tên file đúng format
- [ ] Test tải ZIP xuống
- [ ] Giải nén và kiểm tra nội dung
- [ ] Đọc README và CSV
- [ ] Xác nhận mọi thứ OK

### Sau khi khảo sát kết thúc:

- [ ] Tải xuống tất cả file (ZIP)
- [ ] Backup vào drive/server
- [ ] Verify số lượng file
- [ ] Kiểm tra dung lượng
- [ ] Archive theo quy định
- [ ] Document lại nếu cần
- [ ] Clean up file cũ (sau khi backup)

## 🎉 Tóm tắt

### Để thiết lập:
1. Edit survey
2. Chọn "File Organization"
3. Save

### Để tải xuống:
1. Vào Summary page
2. Click nút download (xanh dương)
3. Nhận file ZIP

### Format tên file:
- **By Response**: Q{question}_{time}_{name}
- **By Question**: R{response}_{time}_{name}

### Nội dung ZIP:
- Tất cả files
- README.txt (thông tin)
- file_list.csv (danh sách)

**Đơn giản, rõ ràng, hiệu quả!** 🚀

---

*Tính năng này giúp quản lý file upload dễ dàng và chuyên nghiệp hơn.*

**Version:** 1.0 | **Date:** 2025-01-02 | **Status:** ✅ Hoạt động tốt
