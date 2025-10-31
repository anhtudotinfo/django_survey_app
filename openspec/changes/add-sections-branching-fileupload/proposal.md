# Proposal: Add Sections, Branch Logic, and File Upload

## Why

Hiện tại, ứng dụng khảo sát hiển thị tất cả câu hỏi trên một trang duy nhất, không có khả năng:
- Chia nhỏ khảo sát dài thành nhiều section để dễ quản lý và trải nghiệm người dùng tốt hơn
- Định tuyến động dựa trên câu trả lời của người dùng (conditional branching)
- Lưu tiến trình và cho phép người dùng tiếp tục sau
- Upload file như hình ảnh, tài liệu

Các tính năng này là tiêu chuẩn trong các công cụ khảo sát hiện đại như Google Forms và sẽ cải thiện đáng kể tính linh hoạt và trải nghiệm người dùng của ứng dụng.

## What Changes

- **Thêm Section Model**: Nhóm câu hỏi thành các section logic với khả năng pagination
- **Thêm Draft Response System**: Lưu tiến trình để người dùng có thể quay lại và tiếp tục
- **Thêm Branch Logic**: Định tuyến có điều kiện cho phép tự động chuyển đến section khác dựa trên câu trả lời
- **Thêm File Upload Field Type**: Loại câu hỏi mới cho phép upload file với validation và lưu trữ an toàn
- **Cập nhật UI**: Multi-step form với progress indicator và navigation

## Impact

### Affected Specs
- `survey-sections`: New capability for organizing questions into sections
- `survey-progress-tracking`: New capability for saving and resuming surveys
- `survey-branch-logic`: New capability for conditional navigation
- `survey-field-types`: Modified to add file upload type

### Affected Code
- `djf_surveys/models.py`: Thêm Section, DraftResponse, BranchRule, cập nhật Question với file field
- `djf_surveys/views.py`: Cập nhật logic để xử lý sections, navigation, draft saving
- `djf_surveys/forms.py`: Thêm file upload handling, section-based form generation
- `djf_surveys/admin.py`: Interface quản lý sections và branch rules
- `templates/`: Thêm multi-step UI với progress tracking
- `settings.py`: Cấu hình file upload (MEDIA_ROOT, allowed types, size limits)

### Breaking Changes
Không có breaking changes. Tất cả khảo sát hiện có sẽ hoạt động như cũ (tất cả câu hỏi được coi là một section duy nhất). Các tính năng mới là opt-in.

### Migration Path
- Khảo sát hiện có tự động tạo một section mặc định chứa tất cả câu hỏi
- Admin có thể dần dần tổ chức lại thành nhiều sections
- Branch logic chỉ được bật khi admin cấu hình rules
