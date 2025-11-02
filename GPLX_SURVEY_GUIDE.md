# Hướng dẫn Khảo sát GPLX (Giấy Phép Lái Xe)

## 📊 Tổng quan

Khảo sát **KHAI BÁO GIẤY PHÉP LÁI XE MÔ TÔ** đã được tạo thành công với đầy đủ tính năng:

- **Tên khảo sát:** KHAI BÁO GIẤY PHÉP LÁI XE MÔ TÔ
- **Slug:** `gplx-declaration`
- **Số sections:** 6 sections
- **Số câu hỏi:** 31 questions
- **Loại khảo sát:** Multi-section với branching logic

## 🌐 URLs để truy cập

### 1. Admin Preview (Quản trị viên)
```
http://127.0.0.1:8000/admin/survey/gplx-declaration/
```
Xem và chỉnh sửa cấu trúc khảo sát.

### 2. Fill Survey (Người dùng)
```
http://127.0.0.1:8000/create/gplx-declaration/
```
Điền khảo sát (cho phép anonymous user).

### 3. View Results (Xem kết quả)
```
http://127.0.0.1:8000/detail/gplx-declaration/
```
Xem danh sách các câu trả lời đã submit.

## 📁 Cấu trúc Sections

### Section 1: Hướng dẫn & Thông tin người khai (8 câu hỏi)
**Mục đích:** Thu thập thông tin cá nhân của người khai báo

Các trường:
1. **Họ và tên** - Text (bắt buộc)
2. **Số CCCD/CMND** - Text (bắt buộc, 9 hoặc 12 số)
3. **Ngày tháng năm sinh** - Date picker (bắt buộc)
4. **Giới tính** - Radio: Nam/Nữ (bắt buộc)
5. **Số điện thoại liên hệ** - Text (bắt buộc)
6. **Địa chỉ thường trú** - Textarea (bắt buộc)
7. **Địa chỉ tạm trú** - Textarea (tùy chọn)
8. **Tổ dân phố** - Dropdown 262 tổ (bắt buộc)

### Section 2: Chọn số lượng GPLX (1 câu hỏi - BRANCHING)
**Mục đích:** Xác định số lượng GPLX cần khai báo

**Câu hỏi:** "Anh/chị có bao nhiêu giấy phép lái xe mô tô đang giữ hoặc đã cấp trước đây?"

**Lựa chọn:**
- ☑ 1 GPLX → Chuyển đến Section 3 (GPLX 1)
- ☑ 2 GPLX → Qua Section 3, 4 (GPLX 1, 2)
- ☑ 3 GPLX → Qua Section 3, 4, 5 (GPLX 1, 2, 3)

**Branching Logic:** Dựa vào lựa chọn, hệ thống sẽ hiển thị các section GPLX tương ứng.

### Section 3, 4, 5: Thông tin GPLX (mỗi section 7 câu hỏi)
**Mục đích:** Thu thập thông tin chi tiết từng GPLX

Mỗi section GPLX có các trường:
1. **Số GPLX** - Text (bắt buộc)
2. **Hạng GPLX** - Dropdown: A1/A2/A3/A4 (bắt buộc)
3. **Ngày cấp** - Date picker (bắt buộc)
4. **Nơi cấp** - Text (bắt buộc, VD: Sở GTVT Đà Nẵng)
5. **Tình trạng GPLX** - Radio (bắt buộc):
   - Còn sử dụng
   - Đã đổi sang PET
   - Mất
   - Hết hạn
6. **Ảnh mặt trước GPLX** - File upload (bắt buộc, .jpg/.png ≤5MB)
7. **Ảnh mặt sau GPLX** - File upload (tùy chọn)

### Section 6: Cam kết (1 câu hỏi)
**Mục đích:** Xác nhận tính chính xác của thông tin

**Checkbox:** "Tôi cam kết thông tin kê khai là đúng sự thật và đồng ý để Công an phường An Khê sử dụng dữ liệu này phục vụ công tác làm sạch, đồng bộ và quản lý giấy phép lái xe"

## ✨ Tính năng đặc biệt

### 1. Multi-Section Survey
- Khảo sát được chia thành 6 sections độc lập
- Progress bar hiển thị tiến độ
- Nút Previous/Next để điều hướng giữa các sections

### 2. Branching Logic
- Section 2 có branching logic dựa trên số lượng GPLX được chọn
- Chỉ hiển thị số section GPLX tương ứng với lựa chọn

### 3. File Upload
- Hỗ trợ upload ảnh GPLX (mặt trước/sau)
- Giới hạn: .jpg, .png, tối đa 5MB
- Lưu trữ trong thư mục media/survey_files/

### 4. Draft Save (Lưu nháp)
- Tự động lưu tiến độ khi chuyển section
- Cho phép tiếp tục điền sau (trong vòng 30 ngày)
- Hỗ trợ cả user đã đăng nhập và anonymous user

### 5. Data Export
- Export CSV với đầy đủ các cột câu hỏi
- Nếu câu hỏi không được trả lời, hiển thị "null"
- Header nhất quán cho tất cả dòng

### 6. Anonymous Access
- Cho phép người dùng chưa đăng nhập điền khảo sát
- Tracking bằng session key

## 🔧 Fix đã thực hiện

### 1. Date Serialization Error
**Vấn đề:** TypeError: Object of type date is not JSON serializable

**Nguyên nhân:** Date objects không thể serialize trực tiếp sang JSON khi lưu draft.

**Giải pháp:**
- Thêm chuyển đổi date → ISO string (YYYY-MM-DD) khi lưu draft
- Chuyển đổi ngược ISO string → date object khi load draft
- File: `djf_surveys/draft_service.py`

### 2. Export CSV với đầy đủ câu hỏi
**Vấn đề:** Chỉ export các câu hỏi có câu trả lời, không nhất quán.

**Giải pháp:**
- Build header với TẤT CẢ câu hỏi của survey
- Điền "null" cho câu hỏi chưa được trả lời
- File: `djf_surveys/admins/views.py` - DownloadResponseSurveyView

### 3. Detail Result hiển thị đầy đủ
**Vấn đề:** Chỉ hiển thị các câu hỏi đã được trả lời.

**Giải pháp:**
- Fetch tất cả câu hỏi của survey
- Tạo question_answer_pairs với null cho missing answers
- File: `djf_surveys/views.py` - DetailResultSurveyView

### 4. Translation
- Dịch tất cả văn bản tiếng Uzbek và tiếng Việt sang tiếng Anh
- Views, templates, error messages đều đã được dịch

## 📝 Hướng dẫn sử dụng

### Tạo khảo sát mới
```bash
cd /home/tuna/Desktop/django_survey_app
python3 create_gplx_survey.py
```

Script sẽ:
1. Tạo survey với slug `gplx-declaration`
2. Tạo 6 sections với ordering đúng
3. Tạo 31 câu hỏi với đầy đủ cấu hình
4. Thiết lập branching logic cho section 2

### Test khảo sát

1. **Truy cập trang điền khảo sát:**
   ```
   http://127.0.0.1:8000/create/gplx-declaration/
   ```

2. **Điền thông tin Section 1:**
   - Họ tên, CCCD, ngày sinh, giới tính, điện thoại, địa chỉ, tổ dân phố

3. **Section 2 - Chọn số GPLX:**
   - Chọn 1, 2, hoặc 3 GPLX
   - Hệ thống sẽ hiển thị số section GPLX tương ứng

4. **Điền thông tin GPLX:**
   - Nhập số GPLX, hạng, ngày cấp, nơi cấp, tình trạng
   - Upload ảnh mặt trước (bắt buộc)
   - Upload ảnh mặt sau (tùy chọn)

5. **Cam kết:**
   - Check vào checkbox cam kết

6. **Submit:**
   - Click "Submit" để hoàn tất

### Xem kết quả

1. **Danh sách câu trả lời:**
   ```
   http://127.0.0.1:8000/detail/gplx-declaration/
   ```

2. **Chi tiết 1 câu trả lời:**
   ```
   http://127.0.0.1:8000/detail/result/{answer_id}/
   ```
   - Hiển thị TẤT CẢ câu hỏi (kể cả chưa trả lời)
   - Câu hỏi chưa trả lời hiển thị "null"

3. **Export CSV:**
   ```
   http://127.0.0.1:8000/admin/download/survey/gplx-declaration/
   ```
   - Header đầy đủ tất cả câu hỏi
   - Missing answers hiển thị "null"

## 🎯 Kiểm tra Branching Logic

### Test Case 1: Chọn 1 GPLX
1. Section 1 → Section 2 (chọn "1 GPLX")
2. Section 2 → Section 3 (GPLX 1)
3. Section 3 → Section 6 (Cam kết)
4. ✅ Không hiển thị Section 4, 5

### Test Case 2: Chọn 2 GPLX
1. Section 1 → Section 2 (chọn "2 GPLX")
2. Section 2 → Section 3 (GPLX 1)
3. Section 3 → Section 4 (GPLX 2)
4. Section 4 → Section 6 (Cam kết)
5. ✅ Không hiển thị Section 5

### Test Case 3: Chọn 3 GPLX
1. Section 1 → Section 2 (chọn "3 GPLX")
2. Section 2 → Section 3 (GPLX 1)
3. Section 3 → Section 4 (GPLX 2)
4. Section 4 → Section 5 (GPLX 3)
5. Section 5 → Section 6 (Cam kết)
6. ✅ Hiển thị đầy đủ tất cả sections

## 🐛 Troubleshooting

### Lỗi: Date not JSON serializable
**Giải pháp:** Đã fix trong `draft_service.py`. Nếu vẫn gặp, restart server.

### Lỗi: Section ordering conflict
**Giải pháp:** Xóa survey cũ và chạy lại script:
```python
Survey.objects.filter(slug='gplx-declaration').delete()
python3 create_gplx_survey.py
```

### Lỗi: File upload không hoạt động
**Kiểm tra:**
1. Thư mục `media/` có quyền write
2. Settings có cấu hình MEDIA_ROOT và MEDIA_URL
3. File size ≤ 5MB và đúng format (.jpg, .png)

### Branching không hoạt động
**Kiểm tra:**
1. Question có `enable_branching=True`
2. `branch_config` đã được set đúng format
3. Section IDs trong branch_config tồn tại

## 📚 Technical Details

### Models Used
- **Survey** - Khảo sát chính
- **Section** - Các phần của khảo sát
- **Question** - Câu hỏi
- **UserAnswer** - Câu trả lời của user
- **Answer** - Chi tiết từng câu trả lời
- **DraftResponse** - Lưu nháp

### Key Files
- `create_gplx_survey.py` - Script tạo khảo sát
- `djf_surveys/draft_service.py` - Service lưu/load draft
- `djf_surveys/views.py` - Views xử lý survey
- `djf_surveys/navigation.py` - Logic điều hướng sections
- `djf_surveys/branch_logic.py` - Xử lý branching

### Database Tables
- `djf_surveys_survey`
- `djf_surveys_section`
- `djf_surveys_question`
- `djf_surveys_useranswer`
- `djf_surveys_answer`
- `djf_surveys_draftresponse`

## ✅ Checklist hoàn thành

- [x] Tạo survey với 6 sections
- [x] Tạo 31 câu hỏi với đầy đủ field types
- [x] Thiết lập branching logic ở Section 2
- [x] Hỗ trợ file upload cho ảnh GPLX
- [x] Fix date serialization error
- [x] Export CSV với đầy đủ columns
- [x] Detail view hiển thị tất cả câu hỏi
- [x] Draft save/resume functionality
- [x] Anonymous user access
- [x] Translation sang tiếng Anh

## 🎉 Kết luận

Khảo sát GPLX đã sẵn sàng để sử dụng với đầy đủ tính năng:
- Multi-section với progress tracking
- Branching logic thông minh
- File upload an toàn
- Draft auto-save
- Export data đầy đủ

**Truy cập:** http://127.0.0.1:8000/create/gplx-declaration/
