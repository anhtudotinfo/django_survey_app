# Design: Sections, Branch Logic, and File Upload

## Context

Ứng dụng Django survey hiện tại sử dụng:
- Django 3.x/4.x với class-based views
- PostgreSQL/SQLite database
- Template-based rendering (không phải SPA)
- Model structure: Survey → Question → UserAnswer → Answer

Yêu cầu mới cần thêm:
1. Multi-page surveys với sections
2. Conditional navigation giữa sections
3. Draft/progress tracking
4. File upload capability

## Goals / Non-Goals

### Goals
- Tổ chức câu hỏi thành sections logic
- Navigation có điều kiện dựa trên câu trả lời
- Lưu draft responses để tiếp tục sau
- Upload và lưu trữ file an toàn
- Backward compatibility với surveys hiện có
- Admin-friendly interface để cấu hình

### Non-Goals
- Real-time collaboration
- Complex workflow engine với parallel paths
- File preview/editing trong browser
- Multi-language support (giữ nguyên cấu trúc hiện tại)
- API endpoints (focus on web UI)

## Decisions

### 1. Section Model Design

**Decision**: Thêm `Section` model với ordering và foreign key đến Survey

**Rationale**:
- Đơn giản và rõ ràng
- Dễ query và paginate
- Compatible với Django ORM patterns hiện có

**Schema**:
```python
class Section(BaseModel):
    survey = ForeignKey(Survey)
    name = CharField(max_length=255)
    description = TextField(blank=True)
    ordering = PositiveIntegerField(default=0)
    
class Question(BaseModel):
    # ... existing fields ...
    section = ForeignKey(Section, null=True, blank=True)  # null for backward compat
```

**Alternatives considered**:
- Nested JSON structure: Khó query và maintain
- Separate SectionQuestion through model: Phức tạp hơn cần thiết

### 2. Draft Response System

**Decision**: Session-based draft storage với database backup

**Rationale**:
- Session storage cho quick access
- Database persistence cho long-term
- Cleanup cron job cho expired drafts

**Schema**:
```python
class DraftResponse(BaseModel):
    survey = ForeignKey(Survey)
    user = ForeignKey(User, null=True, blank=True)  # null for anonymous
    session_key = CharField(max_length=40, null=True, blank=True)
    current_section = ForeignKey(Section, null=True)
    data = JSONField()  # {question_id: value}
    expires_at = DateTimeField()
```

**Alternatives considered**:
- Pure session storage: Mất data khi session expire
- Browser localStorage: Không sync across devices

### 3. Branch Logic Implementation

**Decision**: Simple rule-based system với BranchRule model

**Rationale**:
- Đáp ứng 80% use cases với minimal complexity
- Dễ configure qua Django admin
- Có thể extend sau với complex conditions

**Schema**:
```python
class BranchRule(BaseModel):
    section = ForeignKey(Section, related_name='branch_rules')
    condition_question = ForeignKey(Question)
    condition_operator = CharField(choices=['equals', 'not_equals', 'contains', 'in'])
    condition_value = TextField()
    next_section = ForeignKey(Section, related_name='branch_targets', null=True)
    # null next_section = submit survey
    priority = PositiveIntegerField(default=0)  # evaluate in order
```

**Logic Flow**:
1. User completes section
2. Evaluate branch rules by priority
3. First matching rule determines next section
4. If no match, go to next sequential section
5. If next_section is null, submit survey

**Alternatives considered**:
- Complex expression parser: Overkill cho current needs
- Workflow engine: Too heavy, thêm dependencies

### 4. File Upload Handling

**Decision**: Django FileField với custom validation và private storage

**Rationale**:
- Native Django solution
- Secure by default
- Easy to implement và maintain

**Implementation**:
```python
TYPE_FIELD.file = 10  # Add to existing namedtuple

def upload_survey_file(instance, filename):
    return f'survey_uploads/{instance.user_answer.survey.id}/{instance.user_answer.id}/{filename}'

class Answer(BaseModel):
    # ... existing fields ...
    file_value = FileField(upload_to=upload_survey_file, null=True, blank=True)
```

**Security**:
- Validate file types: images (jpg, png, gif), documents (pdf, docx, xlsx)
- Max size: 10MB per file
- Virus scanning hook point for future
- Private storage: chỉ admin access qua view với permission check

**Storage**:
- Development: Local MEDIA_ROOT
- Production: Ready for S3/cloud storage swap

**Alternatives considered**:
- Base64 trong database: Bloat database size
- Separate microservice: Unnecessary complexity

### 5. UI/UX Flow

**Decision**: Progressive enhancement với fallback

**Navigation**:
```
Section 1 (Questions 1-5)
  → [Next] button → Section 2
  → [Save Draft] button (available anytime)
  → Progress bar: Section 1 of 4

Section 2 (Questions 6-10)
  → [Previous] và [Next] buttons
  → Branch logic evaluated on Next
  
Section N (Final)
  → [Previous] và [Submit] buttons
```

**Features**:
- Progress indicator (linear hoặc step-based)
- Draft auto-save mỗi 2 phút
- Validation per section
- Resume draft prompt nếu tồn tại

**Alternatives considered**:
- Single-page with JS tabs: Mất Django form validation
- Full AJAX SPA: Requires rewrite toàn bộ

## Risks / Trade-offs

### Risks

1. **Database migrations cho existing data**
   - Risk: Surveys với nhiều responses có thể slow migration
   - Mitigation: Default section creation via data migration, có thể run offline

2. **Complex branch logic confusion**
   - Risk: Admin tạo circular references hoặc unreachable sections
   - Mitigation: Validation logic trong admin save, warning messages

3. **File storage costs**
   - Risk: Uncontrolled upload có thể tốn storage
   - Mitigation: File size limits, cleanup cron cho old/orphaned files

4. **Performance với large surveys**
   - Risk: Nhiều sections và rules có thể slow evaluation
   - Mitigation: Index appropriate fields, cache section sequence

### Trade-offs

- **Simplicity vs Flexibility**: Chọn simple rule system thay vì expression engine. Có thể extend sau nếu cần.
- **Storage vs Features**: File uploads tăng storage nhưng là essential feature.
- **Complexity**: Thêm 3-4 models nhưng giữ backward compatibility.

## Migration Plan

### Phase 1: Database Setup (Day 1-2)
1. Tạo migrations cho Section, DraftResponse, BranchRule models
2. Data migration: tạo default section cho mỗi existing survey
3. Link existing questions đến default sections
4. Test rollback

### Phase 2: Core Implementation (Day 3-5)
1. Update forms để handle sections
2. Implement section navigation logic
3. Draft save/load functionality
4. Branch rule evaluation
5. File upload field type

### Phase 3: UI/Admin (Day 6-7)
1. Multi-step form templates
2. Progress indicators
3. Admin interfaces cho sections và rules
4. Testing với existing surveys

### Phase 4: Testing & Polish (Day 8-10)
1. Unit tests cho models và logic
2. Integration tests cho navigation flows
3. Manual QA với various scenarios
4. Performance testing
5. Documentation

### Rollback Plan
- Migrations có reverse operations
- Feature flag: `SURVEY_ENABLE_SECTIONS` setting
- Default behavior: single section (như hiện tại)

## Open Questions

1. **File retention policy**: Giữ files bao lâu sau khi survey deleted?
   - Proposed: 90 days, configurable setting
   
2. **Draft expiration**: Bao lâu drafts tự động xóa?
   - Proposed: 30 days, configurable
   
3. **Max sections per survey**: Có nên limit không?
   - Proposed: 20 sections (reasonable limit)

4. **Branch rule UI**: Admin inline hoặc separate page?
   - Proposed: Inline trong Section admin với TabularInline

5. **Anonymous user drafts**: Xử lý như thế nào khi session expire?
   - Proposed: Show warning, offer to save with email for retrieval
