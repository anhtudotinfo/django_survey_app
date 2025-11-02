# Design Document: Improved Survey UI and File Upload Field

**Change ID**: `improve-survey-ui-fileupload`  
**Status**: Draft  
**Last Updated**: 2025-10-31

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Survey Builder UI Components              │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │      │
│  │  │ Section  │  │ Question │  │ Flow Chart   │   │      │
│  │  │ Manager  │  │ Builder  │  │ Visualizer   │   │      │
│  │  └──────────┘  └──────────┘  └──────────────┘   │      │
│  │                                                   │      │
│  │  ┌──────────────────────────────────────────┐   │      │
│  │  │   File Upload Configuration Widget       │   │      │
│  │  └──────────────────────────────────────────┘   │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                  │
│                          │ AJAX/Fetch API                   │
│                          ▼                                  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                   Django Backend (Server)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │            Admin Views & API Endpoints           │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │      │
│  │  │ Survey   │  │ Section  │  │ Question     │   │      │
│  │  │ CRUD     │  │ CRUD     │  │ CRUD + File  │   │      │
│  │  └──────────┘  └──────────┘  └──────────────┘   │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                  │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Models & Business Logic                  │      │
│  │  Survey, Section, Question, SectionBranch        │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                  │
│  ┌──────────────────────────────────────────────────┐      │
│  │         Database (PostgreSQL/SQLite)             │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Section Manager Component

**Purpose**: Manage multiple survey sections with drag-and-drop reordering AND question redistribution between sections

**Key Features**:
- Drag-and-drop sections for reordering
- Drag-and-drop questions between sections
- Unassigned questions area for questions without a section
- Question counter showing total and per-section counts
- CRUD operations for sections (Create, Read, Update, Delete)
- Visual drop zones with feedback

**Technologies**:
- Alpine.js for reactive state management
- Sortable.js for drag-and-drop (sections AND questions)
- TailwindCSS for styling

**Component Structure**:
```html
<div x-data="sectionManager()" class="section-manager">
    <!-- Section List -->
    <div class="sections-list" x-ref="sortable">
        <template x-for="section in sections" :key="section.id">
            <div class="section-item" :data-section-id="section.id">
                <!-- Section Header -->
                <div class="section-header">
                    <button @click="toggleSection(section.id)">
                        <svg x-show="section.expanded">▼</svg>
                        <svg x-show="!section.expanded">▶</svg>
                    </button>
                    <span x-text="section.name"></span>
                    <div class="drag-handle">⋮</div>
                </div>
                
                <!-- Section Content (Collapsible) -->
                <div x-show="section.expanded" class="section-content">
                    <!-- Questions List -->
                    <div x-for="question in section.questions">
                        <!-- Question Item -->
                    </div>
                    
                    <button @click="addQuestion(section.id)">
                        + Add Question
                    </button>
                    
                    <!-- Branch Configuration -->
                    <div class="branch-config">
                        Branches to: 
                        <select x-model="section.nextSection">
                            <option value="">End Survey</option>
                            <option x-for="s in sections" :value="s.id">
                                <span x-text="s.name"></span>
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </template>
    </div>
    
    <button @click="addSection()">+ Add Section</button>
</div>

<script>
function sectionManager() {
    return {
        sections: [],
        
        init() {
            // Initialize Sortable.js
            const sortable = new Sortable(this.$refs.sortable, {
                handle: '.drag-handle',
                animation: 150,
                onEnd: (evt) => {
                    this.reorderSections(evt.oldIndex, evt.newIndex);
                }
            });
            
            // Load existing sections
            this.loadSections();
        },
        
        async loadSections() {
            const response = await fetch(`/admin/survey/${surveyId}/sections/`);
            this.sections = await response.json();
        },
        
        toggleSection(sectionId) {
            const section = this.sections.find(s => s.id === sectionId);
            section.expanded = !section.expanded;
        },
        
        async addSection() {
            const response = await fetch('/admin/section/create/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    survey_id: surveyId,
                    name: 'New Section',
                    ordering: this.sections.length
                })
            });
            const newSection = await response.json();
            this.sections.push(newSection);
        },
        
        async reorderSections(oldIndex, newIndex) {
            const section = this.sections[oldIndex];
            this.sections.splice(oldIndex, 1);
            this.sections.splice(newIndex, 0, section);
            
            // Update ordering on backend
            await this.saveOrdering();
        },
        
        async saveOrdering() {
            await fetch('/admin/sections/reorder/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    sections: this.sections.map((s, idx) => ({
                        id: s.id,
                        ordering: idx
                    }))
                })
            });
        }
    }
}
</script>
```

### 2. File Upload Question Type Component

**Purpose**: Allow users to configure file upload questions

**Component Structure**:
```html
<div x-data="fileUploadConfig()" class="file-upload-config">
    <!-- File Type Selection -->
    <div class="file-types">
        <h4>Allowed File Types:</h4>
        <label>
            <input type="checkbox" x-model="allowedTypes" value="pdf">
            PDF
        </label>
        <label>
            <input type="checkbox" x-model="allowedTypes" value="doc">
            DOC/DOCX
        </label>
        <label>
            <input type="checkbox" x-model="allowedTypes" value="image">
            Images (JPG, PNG, GIF)
        </label>
        <label>
            <input type="checkbox" x-model="allowedTypes" value="excel">
            Excel (XLS, XLSX)
        </label>
        <label>
            <input type="checkbox" x-model="allowedTypes" value="other">
            Other: <input type="text" x-model="customTypes" placeholder=".txt, .csv">
        </label>
    </div>
    
    <!-- Max File Size -->
    <div class="max-size">
        <label>
            Max File Size:
            <input type="number" x-model="maxSize" min="1" max="100"> MB
        </label>
    </div>
    
    <!-- Multiple Files -->
    <div class="multiple-files">
        <label>
            <input type="checkbox" x-model="allowMultiple">
            Allow Multiple Files
        </label>
        <div x-show="allowMultiple">
            <label>
                Max Files:
                <input type="number" x-model="maxFiles" min="1" max="10">
            </label>
        </div>
    </div>
    
    <!-- Preview -->
    <div class="preview">
        <h4>Preview:</h4>
        <div class="form-group">
            <label x-text="questionLabel"></label>
            <input type="file" 
                   :accept="getAcceptAttribute()"
                   :multiple="allowMultiple">
            <small x-text="getHelpText()"></small>
        </div>
    </div>
</div>

<script>
function fileUploadConfig() {
    return {
        allowedTypes: ['pdf', 'doc'],
        customTypes: '',
        maxSize: 5,
        allowMultiple: false,
        maxFiles: 3,
        questionLabel: 'Upload your file',
        
        getAcceptAttribute() {
            const typeMap = {
                'pdf': '.pdf',
                'doc': '.doc,.docx',
                'image': 'image/*',
                'excel': '.xls,.xlsx'
            };
            
            let accept = this.allowedTypes
                .filter(t => t !== 'other')
                .map(t => typeMap[t])
                .join(',');
            
            if (this.allowedTypes.includes('other') && this.customTypes) {
                accept += ',' + this.customTypes;
            }
            
            return accept;
        },
        
        getHelpText() {
            const types = this.allowedTypes.map(t => t.toUpperCase()).join(', ');
            let text = `Accepted: ${types} (Max ${this.maxSize}MB)`;
            
            if (this.allowMultiple) {
                text += ` - Up to ${this.maxFiles} files`;
            }
            
            return text;
        },
        
        getConfig() {
            return {
                type: 'file',
                allowed_types: this.allowedTypes,
                custom_types: this.customTypes,
                max_size: this.maxSize * 1024 * 1024, // Convert to bytes
                allow_multiple: this.allowMultiple,
                max_files: this.maxFiles
            };
        }
    }
}
</script>
```

### 3. Flow Visualization Component

**Purpose**: Display interactive flowchart of survey sections and branching

**Technology**: D3.js or simple SVG generation

**Component Structure**:
```javascript
class SurveyFlowChart {
    constructor(containerId, surveyData) {
        this.container = document.getElementById(containerId);
        this.surveyData = surveyData;
        this.svg = null;
        this.zoom = null;
    }
    
    render() {
        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', 600);
        
        // Add zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.5, 2])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        // Create main group
        this.g = this.svg.append('g');
        
        // Calculate layout
        const layout = this.calculateLayout();
        
        // Draw connections
        this.drawConnections(layout);
        
        // Draw nodes
        this.drawNodes(layout);
    }
    
    calculateLayout() {
        const sections = this.surveyData.sections;
        const layout = [];
        
        // Simple tree layout
        const width = this.container.clientWidth;
        const nodeWidth = 150;
        const nodeHeight = 80;
        const verticalGap = 100;
        
        let currentY = 50;
        
        sections.forEach((section, index) => {
            layout.push({
                id: section.id,
                x: width / 2 - nodeWidth / 2,
                y: currentY,
                width: nodeWidth,
                height: nodeHeight,
                name: section.name,
                branches: section.branches || []
            });
            
            currentY += nodeHeight + verticalGap;
        });
        
        return layout;
    }
    
    drawNodes(layout) {
        const nodes = this.g.selectAll('.section-node')
            .data(layout)
            .enter()
            .append('g')
            .attr('class', 'section-node')
            .attr('transform', d => `translate(${d.x}, ${d.y})`)
            .on('click', (event, d) => this.onNodeClick(d));
        
        // Rectangle
        nodes.append('rect')
            .attr('width', d => d.width)
            .attr('height', d => d.height)
            .attr('rx', 5)
            .attr('fill', '#3b82f6')
            .attr('stroke', '#1e40af')
            .attr('stroke-width', 2);
        
        // Text
        nodes.append('text')
            .attr('x', d => d.width / 2)
            .attr('y', d => d.height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .text(d => d.name);
    }
    
    drawConnections(layout) {
        const connections = [];
        
        layout.forEach(node => {
            node.branches.forEach(branch => {
                const targetNode = layout.find(n => n.id === branch.next_section);
                if (targetNode) {
                    connections.push({
                        source: node,
                        target: targetNode,
                        condition: branch.condition
                    });
                }
            });
        });
        
        // Draw lines
        const lines = this.g.selectAll('.connection')
            .data(connections)
            .enter()
            .append('g')
            .attr('class', 'connection');
        
        lines.append('line')
            .attr('x1', d => d.source.x + d.source.width / 2)
            .attr('y1', d => d.source.y + d.source.height)
            .attr('x2', d => d.target.x + d.target.width / 2)
            .attr('y2', d => d.target.y)
            .attr('stroke', '#6b7280')
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#arrowhead)');
        
        // Add condition labels
        lines.append('text')
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#374151')
            .text(d => d.condition);
    }
    
    onNodeClick(node) {
        // Navigate to section editor
        window.location.href = `/admin/section/${node.id}/edit/`;
    }
    
    detectCircularReferences() {
        const visited = new Set();
        const recursionStack = new Set();
        
        const hasCycle = (sectionId) => {
            visited.add(sectionId);
            recursionStack.add(sectionId);
            
            const section = this.surveyData.sections.find(s => s.id === sectionId);
            if (!section) return false;
            
            for (const branch of section.branches || []) {
                if (!visited.has(branch.next_section)) {
                    if (hasCycle(branch.next_section)) {
                        return true;
                    }
                } else if (recursionStack.has(branch.next_section)) {
                    return true;
                }
            }
            
            recursionStack.delete(sectionId);
            return false;
        };
        
        for (const section of this.surveyData.sections) {
            if (!visited.has(section.id)) {
                if (hasCycle(section.id)) {
                    return true;
                }
            }
        }
        
        return false;
    }
}
```

## Database Schema

### No Changes Required

The existing schema already supports all features:

```python
# Existing models (no changes needed)

class Survey(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # ... other fields

class Section(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ordering = models.IntegerField(default=0)
    # ... other fields

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    label = models.CharField(max_length=500)
    type_field = models.IntegerField(choices=TYPE_FIELD_CHOICES)
    # type_field = 10 for file upload (already exists)
    ordering = models.IntegerField(default=0)
    # ... other fields

class SectionBranch(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    condition_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    condition_operator = models.CharField(max_length=10)
    condition_value = models.CharField(max_length=255)
    next_section = models.ForeignKey(Section, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)
```

## API Endpoints

### New/Modified Endpoints

```python
# djf_surveys/admins/urls.py

urlpatterns = [
    # Existing endpoints...
    
    # New endpoints for enhanced UI
    path('api/survey/<slug:slug>/sections/', SurveySecti onsAPIView.as_view(), name='api-survey-sections'),
    path('api/section/create/', SectionCreateAPIView.as_view(), name='api-section-create'),
    path('api/section/<int:pk>/update/', SectionUpdateAPIView.as_view(), name='api-section-update'),
    path('api/sections/reorder/', SectionReorderAPIView.as_view(), name='api-sections-reorder'),
    path('api/question/create/', QuestionCreateAPIView.as_view(), name='api-question-create'),
    path('api/survey/<slug:slug>/flow/', SurveyFlowAPIView.as_view(), name='api-survey-flow'),
]
```

### API Response Examples

**GET /api/survey/{slug}/sections/**
```json
{
  "survey": {
    "id": 1,
    "name": "Student Feedback 2024",
    "slug": "student-feedback-2024"
  },
  "sections": [
    {
      "id": 1,
      "name": "General Information",
      "ordering": 0,
      "questions": [
        {
          "id": 1,
          "label": "Full Name",
          "type_field": 0,
          "ordering": 0,
          "required": true
        },
        {
          "id": 2,
          "label": "Student ID",
          "type_field": 0,
          "ordering": 1,
          "required": true
        }
      ],
      "branches": []
    },
    {
      "id": 2,
      "name": "Course Evaluation",
      "ordering": 1,
      "questions": [
        {
          "id": 3,
          "label": "How was the course?",
          "type_field": 2,
          "ordering": 0,
          "required": true,
          "choices": ["Excellent", "Good", "Average", "Poor"]
        }
      ],
      "branches": [
        {
          "condition_question": 3,
          "condition_operator": "equals",
          "condition_value": "Excellent",
          "next_section": 3
        },
        {
          "condition_question": 3,
          "condition_operator": "equals",
          "condition_value": "Poor",
          "next_section": 4
        }
      ]
    }
  ]
}
```

**POST /api/question/create/**
```json
{
  "survey_id": 1,
  "section_id": 2,
  "label": "Please upload your transcript",
  "type_field": 10,
  "help_text": "Accepted: PDF, DOC, DOCX (Max 5MB)",
  "required": true,
  "ordering": 3,
  "file_config": {
    "allowed_types": ["pdf", "doc"],
    "max_size": 5242880,
    "allow_multiple": false
  }
}
```

## UI/UX Design

### Color Scheme

```css
:root {
    --primary: #3b82f6;      /* Blue for primary actions */
    --primary-dark: #1e40af;  /* Darker blue for hover */
    --secondary: #10b981;     /* Green for success */
    --danger: #ef4444;        /* Red for delete/errors */
    --warning: #f59e0b;       /* Orange for warnings */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-700: #374151;
    --gray-900: #111827;
}
```

### Component States

**Section Item States**:
- Default: Gray background, subtle border
- Hover: Light blue background
- Dragging: Shadow, semi-transparent
- Expanded: Darker background, content visible
- Collapsed: Lighter background, content hidden
- Invalid: Red border, error icon

**Question Item States**:
- Normal: White background
- Hover: Light gray background
- Selected: Blue border
- Required: Red asterisk
- Invalid: Red border, error message

### Responsive Design

```css
/* Desktop (>= 1024px) */
@media (min-width: 1024px) {
    .survey-builder {
        grid-template-columns: 300px 1fr 250px;
        /* Sidebar | Main | Properties Panel */
    }
}

/* Tablet (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
    .survey-builder {
        grid-template-columns: 250px 1fr;
        /* Sidebar | Main (No properties panel) */
    }
}

/* Mobile (<= 767px) */
@media (max-width: 767px) {
    .survey-builder {
        grid-template-columns: 1fr;
        /* Stack everything vertically */
    }
    
    .drag-handle {
        display: none; /* No drag on mobile */
    }
    
    .flow-view {
        display: none; /* Too complex for mobile */
    }
}
```

## Performance Optimization

### 1. Lazy Loading

```javascript
// Load sections on demand
async function loadSection(sectionId) {
    if (loadedSections.has(sectionId)) {
        return loadedSections.get(sectionId);
    }
    
    const response = await fetch(`/api/section/${sectionId}/`);
    const section = await response.json();
    
    loadedSections.set(sectionId, section);
    return section;
}
```

### 2. Debounced Autosave

```javascript
const debouncedSave = debounce(async (data) => {
    await fetch('/api/survey/save/', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}, 1000); // Save after 1 second of inactivity
```

### 3. Virtual Scrolling

```javascript
// For surveys with 100+ questions
function virtualScrollQuestions(container, questions, itemHeight) {
    const visibleCount = Math.ceil(container.clientHeight / itemHeight);
    const startIndex = Math.floor(container.scrollTop / itemHeight);
    const endIndex = startIndex + visibleCount;
    
    // Only render visible questions
    return questions.slice(startIndex, endIndex + 1);
}
```

## Security Considerations

### 1. File Upload Security

```python
# Validate file types
ALLOWED_FILE_TYPES = {
    'pdf': ['application/pdf'],
    'doc': ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    'image': ['image/jpeg', 'image/png', 'image/gif'],
    'excel': ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
}

def validate_file_upload(file, allowed_types, max_size):
    # Check file size
    if file.size > max_size:
        raise ValidationError(f'File too large. Max size: {max_size / (1024*1024)}MB')
    
    # Check file type
    import magic
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    
    valid_types = []
    for type_key in allowed_types:
        valid_types.extend(ALLOWED_FILE_TYPES.get(type_key, []))
    
    if file_type not in valid_types:
        raise ValidationError('File type not allowed')
    
    # Scan for malware (optional, requires antivirus integration)
    # scan_file_for_malware(file)
    
    return True
```

### 2. CSRF Protection

All AJAX requests include CSRF token:

```javascript
fetch('/api/section/create/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(data)
});
```

### 3. Permission Checks

```python
@method_decorator(staff_member_required, name='dispatch')
class SectionCreateAPIView(CreateView):
    def post(self, request, *args, **kwargs):
        # Verify user has permission to edit survey
        survey = get_object_or_404(Survey, pk=request.POST.get('survey_id'))
        if not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Create section
        # ...
```

## Testing Strategy

### 1. Unit Tests

```python
# tests/test_file_upload_component.py

class FileUploadComponentTests(TestCase):
    def test_file_upload_question_creation(self):
        """Test creating a file upload question"""
        survey = Survey.objects.create(name='Test Survey')
        section = Section.objects.create(survey=survey, name='Test Section')
        
        question = Question.objects.create(
            survey=survey,
            section=section,
            label='Upload file',
            type_field=TYPE_FIELD.file,
            required=True
        )
        
        self.assertEqual(question.type_field, TYPE_FIELD.file)
    
    def test_file_validation(self):
        """Test file type validation"""
        # ... test file upload validation
```

### 2. Integration Tests

```python
# tests/test_survey_builder_integration.py

class SurveyBuilderIntegrationTests(TestCase):
    def test_create_multi_section_survey(self):
        """Test creating survey with multiple sections via API"""
        client = Client()
        client.login(username='admin', password='admin')
        
        # Create survey
        response = client.post('/api/survey/create/', {
            'name': 'Test Survey',
            'description': 'Test Description'
        })
        survey_id = response.json()['id']
        
        # Add sections
        section1 = client.post('/api/section/create/', {
            'survey_id': survey_id,
            'name': 'Section 1'
        })
        
        # ... verify sections created correctly
```

### 3. End-to-End Tests

```javascript
// tests/e2e/survey_builder.spec.js

describe('Survey Builder', () => {
    it('should create multi-section survey with file upload', () => {
        cy.visit('/admin/survey/create/');
        
        // Enter survey details
        cy.get('input[name="name"]').type('Student Survey');
        
        // Add section
        cy.contains('Add Section').click();
        cy.get('input[name="section_name"]').type('Documents');
        
        // Add file upload question
        cy.contains('Add Question').click();
        cy.get('[data-question-type="file"]').click();
        cy.get('input[name="question_label"]').type('Upload Transcript');
        
        // Configure file upload
        cy.get('input[value="pdf"]').check();
        cy.get('input[name="max_size"]').clear().type('10');
        
        // Save
        cy.contains('Save Survey').click();
        
        // Verify
        cy.contains('Survey created successfully');
    });
});
```

## Deployment Plan

### Phase 1: Backend API (Week 1)
1. Create new API endpoints
2. Add file upload validation
3. Unit tests
4. Deploy to staging

### Phase 2: File Upload UI (Week 1-2)
1. Add file upload button to question type selector
2. Create configuration modal
3. Update form preview
4. Integration tests
5. Deploy to staging

### Phase 3: Section Builder (Week 2-3)
1. Build collapsible section component
2. Add drag-and-drop functionality
3. Implement inline editing
4. Integration tests
5. Deploy to staging

### Phase 4: Flow Visualization (Week 3-4)
1. Create flowchart component
2. Add interaction handlers
3. Implement circular reference detection
4. UI tests
5. Deploy to staging

### Phase 5: Production Deployment (Week 5)
1. User acceptance testing
2. Performance testing
3. Security audit
4. Documentation
5. Deploy to production
6. Monitor and gather feedback

## Rollback Plan

If issues are discovered in production:

1. **Immediate**: Feature flag to disable new UI, fallback to old interface
2. **Short-term**: Hotfix critical bugs, redeploy
3. **Long-term**: If unfixable, rollback entire feature and reassess

```python
# settings.py
FEATURE_FLAGS = {
    'enhanced_survey_builder': os.getenv('ENHANCED_BUILDER', 'true').lower() == 'true',
    'file_upload_ui': os.getenv('FILE_UPLOAD_UI', 'true').lower() == 'true',
}

# In template
{% if feature_flags.enhanced_survey_builder %}
    {% include 'djf_surveys/admins/enhanced_builder.html' %}
{% else %}
    {% include 'djf_surveys/admins/legacy_builder.html' %}
{% endif %}
```

## Conclusion

This design provides a comprehensive, implementable solution for:
1. Enhanced multi-section survey creation UI
2. File upload field type integration
3. Visual flow builder
4. Improved user experience

The design is modular, performant, secure, and maintains backward compatibility with existing surveys.
