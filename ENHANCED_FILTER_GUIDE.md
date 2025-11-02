# Hướng Dẫn Sử Dụng Tính Năng Filter Nâng Cao

## Tổng Quan

Trang Summary (dashboard/summary/survey/<slug>) đã được nâng cấp với các tính năng filter và download mới:

### Tính Năng Mới:

1. **Filter theo khoảng thời gian (Date Range)**
   - Lọc câu trả lời từ ngày đến ngày
   - Ưu tiên cao hơn filter Year/Month

2. **Filter theo câu hỏi cụ thể**
   - Chọn câu hỏi nào muốn xem/download
   - Select All / Deselect All nhanh chóng
   - Hiển thị tối đa 60% chiều cao màn hình với scroll

3. **Download với tất cả filter**
   - Download CSV với đầy đủ filter đã chọn
   - Thông tin filter được ghi trong file CSV
   - Tên file tự động chứa thông tin ngày tháng

## Chi Tiết Các Filter

### 1. Date Range Filter (Ưu Tiên Cao Nhất)

**Vị trí:** Khung màu xanh dương ở đầu form

**Các trường:**
- **From Date (Từ ngày):** Ngày bắt đầu (YYYY-MM-DD)
- **To Date (Đến ngày):** Ngày kết thúc (YYYY-MM-DD)
- **Nút Clear:** Xóa date range

**Cách hoạt động:**
- Nếu chọn date range → Year/Month filters sẽ bị bỏ qua
- To Date sẽ bao gồm cả ngày đó (hết 23:59:59)
- Có thể chỉ chọn From Date hoặc To Date
- Ví dụ: 
  - From: 2024-01-01, To: 2024-03-31 → Q1 2024
  - From: 2024-06-01, To: (empty) → Từ 1/6/2024 đến hiện tại

### 2. Course/Direction Filter

**Vị trí:** Dropdown đầu tiên trong khung filters chính

**Chức năng:**
- Lọc theo khóa học/lớp học
- "All Courses" = không filter

### 3. Year & Month Filters

**Vị trí:** Dropdown thứ 2 và 3 trong khung filters chính

**Chức năng:**
- Chỉ hoạt động khi KHÔNG có Date Range
- Year: Lọc theo năm
- Month: Lọc theo tháng (cần có Year để hiệu quả)

### 4. Question Filter (Mới)

**Vị trí:** Khung màu xanh lá ở cuối form

**Các tính năng:**
- **Checkbox list:** Danh sách tất cả câu hỏi trong survey
- **Select All:** Chọn tất cả câu hỏi
- **Deselect All:** Bỏ chọn tất cả câu hỏi
- **Scroll:** Nếu nhiều câu hỏi, có thanh scroll
- **Default:** Nếu không chọn gì = hiển thị tất cả

## Các Nút Hành Động

### 1. Apply Filters (Áp dụng Filter)
**Icon:** 🔽 Filter  
**Màu:** Xanh dương  
**Chức năng:**
- Áp dụng tất cả filters đã chọn
- Cập nhật charts và statistics
- URL sẽ chứa query parameters

### 2. Download Filtered Data
**Icon:** ⬇ Download  
**Màu:** Xanh lá  
**Chức năng:**
- Download CSV với filters hiện tại
- File bao gồm:
  - Header với thông tin filter
  - Cột: User, Direction, Submitted Time, Questions
  - File URLs cho file upload questions
  - Tên file: `survey-slug_from-DATE_to-DATE.csv`

### 3. Reset All Filters
**Icon:** ↻ Reset  
**Màu:** Xám  
**Chức năng:**
- Xóa tất cả filters
- Reload trang không có query parameters
- Hiển thị tất cả dữ liệu

## Ví Dụ Sử Dụng

### Ví dụ 1: Xem dữ liệu Q1 2024
```
1. From Date: 2024-01-01
2. To Date: 2024-03-31
3. Course: (All Courses)
4. Questions: (All)
5. Click "Apply Filters"
```

### Ví dụ 2: Download chỉ 3 câu hỏi cụ thể
```
1. Date Range: (empty) - tất cả thời gian
2. Course: Khóa học ABC
3. Questions: 
   - ✓ Question 1
   - ✓ Question 5
   - ✓ Question 10
4. Click "Download Filtered Data"
```

### Ví dụ 3: Xem tháng 11/2024
```
1. Date Range: (empty)
2. Year: 2024
3. Month: November
4. Course: (All Courses)
5. Questions: (All)
6. Click "Apply Filters"
```

### Ví dụ 4: Phân tích tuần vừa qua
```
1. From Date: 2024-10-25
2. To Date: 2024-11-01
3. Course: (specific course)
4. Questions: (chọn câu hỏi quan trọng)
5. Click "Apply Filters" để xem charts
6. Click "Download Filtered Data" để lưu file
```

## File CSV Download

### Cấu trúc file:
```csv
Filters: From: 2024-01-01, To: 2024-03-31, Course: ABC

User,Direction,Submitted Time,Question 1,Question 2,Question 3
john_doe,Course ABC,2024-01-15 10:30:00,Answer 1,Answer 2,http://localhost:8000/download/file/123/
jane_smith,Course ABC,2024-02-20 14:15:00,Answer A,Answer B,N/A
```

### Tên file:
- Không filter: `survey-slug.csv`
- Có date range: `survey-slug_from-2024-01-01_to-2024-03-31.csv`

### Các cột đặc biệt:
- **User:** Username hoặc "Guest"
- **Direction:** Tên khóa học hoặc "N/A"
- **Submitted Time:** YYYY-MM-DD HH:MM:SS
- **File Upload columns:** Full URL để download file

## URL Structure

### View Summary:
```
/dashboard/summary/survey/<slug>/?from_date=2024-01-01&to_date=2024-03-31&questions=1&questions=5&direction=2
```

### Download Filtered:
```
/dashboard/download/filtered/<slug>/?from_date=2024-01-01&to_date=2024-03-31&questions=1&questions=5&direction=2
```

## Thứ Tự Ưu Tiên Filter

1. **Date Range** (cao nhất)
   - Nếu có from_date hoặc to_date
   - Year & Month sẽ bị bỏ qua

2. **Year & Month**
   - Chỉ khi không có Date Range

3. **Direction/Course**
   - Luôn được áp dụng nếu có

4. **Questions**
   - Luôn được áp dụng nếu có
   - Rỗng = tất cả questions

## Technical Details

### Backend Changes:

1. **SummaryResponse class** (`djf_surveys/summary.py`)
   - Thêm parameters: `from_date`, `to_date`, `selected_questions`
   - Cập nhật `get_filtered_queryset()` với date range logic
   - Cập nhật `generate_questions()` để filter questions

2. **DownloadFilteredResponseSurveyView** (`djf_surveys/admins/views.py`)
   - View mới cho download với filters
   - Apply tất cả filters vào queryset
   - Thêm filter info vào CSV header
   - Dynamic filename với date range

3. **SummaryResponseSurveyView** (`djf_surveys/admins/views.py`)
   - Parse date range từ GET params
   - Parse selected questions từ GET params
   - Pass filters vào SummaryResponse
   - Add context cho template

### Frontend Changes:

1. **Template** (`summary.html`)
   - Date range input với date picker
   - Question filter với checkboxes
   - JavaScript functions cho UI interactions
   - Improved button layout

2. **JavaScript Functions:**
   - `clearDateRange()`: Clear date inputs
   - `selectAllQuestions()`: Check all question checkboxes
   - `deselectAllQuestions()`: Uncheck all
   - `resetFilters()`: Reset form và reload
   - `downloadFiltered()`: Build URL và download

### URL Routing:

**New route:** `/dashboard/download/filtered/<slug>/`  
**View:** `DownloadFilteredResponseSurveyView`  
**Name:** `admin_download_filtered_survey`

## Testing

### Test Cases:

1. **No filters:** Hiển thị tất cả data
2. **Date range only:** Filter by dates
3. **Questions only:** Chỉ show selected questions
4. **Combined filters:** All filters together
5. **Download:** Verify CSV content và filename
6. **Reset:** Clear all filters
7. **Select All/Deselect All:** Question checkboxes

### Manual Test:
```
1. Vào: http://127.0.0.1:8000/dashboard/summary/survey/<slug>/
2. Test từng filter riêng lẻ
3. Test kết hợp filters
4. Verify charts update correctly
5. Download và check CSV file
6. Test Reset button
```

## Troubleshooting

### Charts không cập nhật?
- Kiểm tra console log
- Verify Chart.js loaded
- Kiểm tra query parameters trong URL

### Download không hoạt động?
- Check URL trong Network tab
- Verify filters được pass đúng
- Kiểm tra server logs

### Questions không hiển thị?
- Verify survey có questions
- Check `all_questions` trong template context

## Browser Compatibility

- Chrome/Edge: ✓ Full support
- Firefox: ✓ Full support
- Safari: ✓ Full support
- Mobile: ✓ Responsive design

## Notes

- Date picker format: YYYY-MM-DD (ISO 8601)
- Timezone: Server timezone
- Multiple question selection: Hold Ctrl/Cmd
- Max display: Auto scroll nếu >20 questions
