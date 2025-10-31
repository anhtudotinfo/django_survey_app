# Hướng dẫn sử dụng File Upload trong Survey

## ✅ Status: File Upload đã được setup hoàn chỉnh!

Tôi đã tạo sẵn 1 survey test với file upload question.

## 🔍 Kiểm tra Survey

### Survey đã có:
- **Name**: a
- **URL**: http://localhost:8000/create/a/
- **Questions**:
  1. "Your Name" (Text field)
  2. "Please upload your CV (PDF or Word)" (File Upload field) ✓

## 📝 Cách tạo File Upload Question trong Admin

### Bước 1: Truy cập Django Admin
```
URL: http://localhost:8000/admin/
```

### Bước 2: Tạo hoặc chỉnh sửa Question
1. Vào **Surveys** → **Questions** → **Add Question**
2. Hoặc chọn survey → Add question inline

### Bước 3: Chọn Field Type = "File Upload"
```
Survey: [Chọn survey của bạn]
Section: [Chọn section]
Label: "Upload your document"
Type of input field: File Upload  ← QUAN TRỌNG!
Help text: "Accepted: PDF, Word, Excel. Max 10MB"
Required: ✓ (nếu bắt buộc)
```

### Bước 4: Save

## 🎯 Test File Upload

### 1. Mở Survey trong browser:
```
http://localhost:8000/create/a/
```

### 2. Bạn sẽ thấy:
- Text input cho "Your Name"
- **File input** cho "Please upload your CV"
  ```html
  <input type="file" name="field_survey_1" 
         class="w-full p-4 pr-12 text-lg border-gray-500 rounded-lg shadow-sm" 
         required>
  ```

### 3. Test Upload:
- Chọn file (PDF, DOC, DOCX, JPG, PNG, etc.)
- File phải < 10MB
- Click "Next" hoặc "Submit"
- File sẽ được upload và lưu

### 4. Xem kết quả:
- Vào Admin → User Answers → Xem answer
- File sẽ hiển thị dạng link download
- Click vào link để download file

## 🔒 File Upload Settings

Trong `moi/settings.py`:
```python
SURVEY_FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
SURVEY_FILE_ALLOWED_TYPES = [
    'jpg', 'jpeg', 'png', 'gif',  # Images
    'pdf',                          # PDF
    'doc', 'docx',                 # Word
    'xls', 'xlsx',                 # Excel
]
```

## ⚙️ Allowed File Types

### Hiện tại cho phép:
- **Images**: JPG, JPEG, PNG, GIF
- **Documents**: PDF, DOC, DOCX
- **Spreadsheets**: XLS, XLSX

### Thêm file types khác:
Edit `moi/settings.py`:
```python
SURVEY_FILE_ALLOWED_TYPES = [
    'jpg', 'jpeg', 'png', 'gif',
    'pdf', 'doc', 'docx',
    'xls', 'xlsx',
    'txt',  # Text files
    'zip',  # ZIP archives
    # Add more...
]
```

## 🛡️ Security Features

### 1. File Type Validation
- Kiểm tra extension
- Kiểm tra MIME type
- Reject nếu không match

### 2. File Size Limit
- Default: 10MB
- Configurable trong settings
- Error message rõ ràng

### 3. Protected Downloads
- File không public
- Chỉ admin và owner xem được
- URL: `/download/file/<answer_id>/`

### 4. Filename Sanitization
- Remove path traversal attempts
- Clean special characters
- Safe storage path

## 📂 File Storage

### Development:
```
project_root/
  media/
    survey_uploads/
      <survey_id>/
        <user_answer_id>/
          filename.pdf
```

### Production:
- Có thể config S3, Google Cloud Storage
- Change Django's DEFAULT_FILE_STORAGE

## 🐛 Troubleshooting

### Không thấy file input?

#### 1. Check Question Type:
```python
python manage.py shell
>>> from djf_surveys.models import Question, TYPE_FIELD
>>> q = Question.objects.get(id=1)
>>> print(q.type_field)  # Should be 10
>>> print(q.get_type_field_display())  # Should be "File Upload"
```

#### 2. Check Form:
```python
python manage.py shell
>>> from djf_surveys.forms import CreateSurveyForm
>>> from djf_surveys.models import Survey
>>> survey = Survey.objects.first()
>>> section = survey.sections.first()
>>> form = CreateSurveyForm(survey=survey, user=None, current_section=section)
>>> for name, field in form.fields.items():
...     if 'file' in name.lower() or 'FileField' in str(type(field)):
...         print(f'{name}: {type(field).__name__}')
```

#### 3. Check Template:
Template đã có `enctype="multipart/form-data"` trong form tag ✓

#### 4. Browser DevTools:
- F12 → Elements tab
- Search for: `type="file"`
- Should find: `<input type="file" ...>`

### File không upload?

#### Check form enctype:
```html
<form method="post" enctype="multipart/form-data">
  <!-- ↑ MUST HAVE THIS! -->
```

#### Check form data:
```python
# In view.py
def post(self, request, *args, **kwargs):
    print('FILES:', request.FILES)  # Debug
    print('POST:', request.POST)
```

### File quá lớn?

Change max size:
```python
# settings.py
SURVEY_FILE_UPLOAD_MAX_SIZE = 50 * 1024 * 1024  # 50MB
```

## ✅ Verification Checklist

- [x] TYPE_FIELD has 'file' (value=10)
- [x] TYPE_FIELD_CHOICES includes "File Upload"
- [x] FileTypeValidator and FileSizeValidator created
- [x] BaseSurveyForm handles FileField
- [x] CreateSurveyForm.save() handles file_value
- [x] Template has enctype="multipart/form-data"
- [x] Protected download view created
- [x] URL pattern for downloads added
- [x] Test question created
- [x] All validators working

## 🎉 Ready to Use!

Survey với file upload đã sẵn sàng:
**http://localhost:8000/create/a/**

Vào URL trên và bạn sẽ thấy file input field!

## 📞 Support

Nếu vẫn không thấy file input:
1. Restart Django server
2. Clear browser cache
3. Check browser console for errors (F12)
4. Verify Question type_field = 10 (File Upload)
