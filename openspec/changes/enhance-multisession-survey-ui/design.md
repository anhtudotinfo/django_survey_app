# Design: Enhanced Multi-Session Survey Builder UI

**Change ID**: `enhance-multisession-survey-ui`  
**Status**: Proposal  
**Last Updated**: 2025-10-31

## Context

The Django survey application currently supports multi-session surveys through the Section, Question, and BranchRule models. However, the admin interface lacks modern UI components to effectively manage these features. The existing interface:

- Uses basic Django admin forms
- Has no visual section management
- File upload type exists (TYPE_FIELD.file = 10) but is hidden from the UI
- Provides no drag-and-drop capabilities
- Lacks visual feedback for survey flow structure

This design enhances the admin interface to provide an intuitive, modern experience for creating complex multi-session surveys.

## Goals / Non-Goals

### Goals
- Make file upload field type visible and configurable in the UI
- Provide collapsible, drag-and-drop section management
- Enable visual question organization between sections
- Add file upload configuration panel with live preview
- Maintain backward compatibility with existing surveys
- Keep implementation simple using existing tech stack

### Non-Goals
- Respondent-facing UI changes (only admin interface)
- Real-time collaboration features
- Complex workflow engine beyond existing branch rules
- Mobile-first admin interface (desktop-focused, mobile-friendly)
- SPA rewrite (stay with template-based approach)

## Decisions

### 1. Technology Stack

**Decision**: Use Alpine.js for reactive components, Sortable.js for drag-and-drop

**Rationale**:
- Alpine.js is lightweight (15KB), fits Django template philosophy
- Sortable.js is proven, dependency-free drag-and-drop library
- Both work well with existing TailwindCSS styling
- No build step required, can include via CDN
- Minimal JavaScript, progressive enhancement approach

**Alternatives Considered**:
- React/Vue: Too heavy, requires build pipeline, SPA approach conflicts with Django templates
- jQuery UI: Outdated, larger bundle size
- Vanilla JS: More code to maintain, lacks reactivity

**Implementation**:
```html
<!-- In base template -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
```

### 2. File Upload UI Integration

**Decision**: Add file upload to existing modal_choice_field_type.html

**Rationale**:
- Minimal change, uses existing pattern
- File upload type already exists in backend (TYPE_FIELD.file = 10)
- Admins already familiar with modal workflow
- No breaking changes required

**Implementation**:
```html
<!-- In modal_choice_field_type.html -->
<li class="flex">
    <a href="{% url 'djf_surveys:admin_create_question' object.id 10 %}" 
       class="hover:border-blue-500 hover:border-solid hover:bg-white hover:text-blue-500 group w-full flex flex-col items-center justify-center rounded-md border-2 border-slate-300 text-sm leading-6 text-slate-900 font-medium py-3">
        <i class="fas fa-file-upload text-2xl mb-2"></i>
        File Upload
    </a>
</li>
```

**View Context Update**:
```python
# In djf_surveys/admins/views.py
def get_type_field_choices():
    """Return formatted type field choices for template."""
    return [
        {'id': 0, 'label': _('Text'), 'icon': 'fas fa-font'},
        {'id': 1, 'label': _('Number'), 'icon': 'fas fa-hashtag'},
        # ... other types ...
        {'id': 10, 'label': _('File Upload'), 'icon': 'fas fa-file-upload'},
    ]
```

**Alternatives Considered**:
- Separate page for file questions: Breaks existing workflow
- Automatic type detection: Too magical, lacks explicit control

### 3. Section Manager Component

**Decision**: Collapsible section list with inline editing and drag-and-drop

**Component Structure**:
```html
<div x-data="sectionManager()" class="section-manager">
    <!-- Section List -->
    <div class="sections-container space-y-4" x-ref="sectionsContainer">
        <template x-for="(section, index) in sections" :key="section.id">
            <div class="section-card bg-white rounded-lg shadow-sm border border-gray-200"
                 :data-section-id="section.id">
                
                <!-- Section Header -->
                <div class="section-header flex items-center justify-between p-4 cursor-pointer"
                     @click="toggleSection(section.id)">
                    <div class="flex items-center space-x-3">
                        <!-- Drag Handle -->
                        <div class="drag-handle cursor-move text-gray-400 hover:text-gray-600">
                            <i class="fas fa-grip-vertical"></i>
                        </div>
                        
                        <!-- Expand/Collapse Icon -->
                        <button type="button" class="text-gray-500">
                            <i class="fas" :class="section.expanded ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                        </button>
                        
                        <!-- Section Name -->
                        <div x-show="!section.editing" @dblclick="startEditSection(section.id)">
                            <h3 class="text-lg font-semibold" x-text="section.name"></h3>
                            <p class="text-sm text-gray-500" x-text="section.description" x-show="section.description"></p>
                        </div>
                        
                        <!-- Inline Edit -->
                        <div x-show="section.editing" class="space-y-2">
                            <input type="text" x-model="section.name" 
                                   @blur="saveSection(section)" 
                                   @keydown.enter="saveSection(section)"
                                   @keydown.escape="cancelEdit(section)"
                                   class="px-3 py-1 border rounded">
                            <textarea x-model="section.description" 
                                      @blur="saveSection(section)"
                                      placeholder="Description (optional)"
                                      rows="2"
                                      class="px-3 py-1 border rounded w-full"></textarea>
                        </div>
                    </div>
                    
                    <!-- Question Count Badge -->
                    <div class="flex items-center space-x-3">
                        <span class="badge bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                            <i class="fas fa-question-circle"></i>
                            <span x-text="section.questions.length"></span> questions
                        </span>
                        
                        <!-- Delete Button -->
                        <button @click.stop="deleteSection(section.id)" 
                                class="text-red-500 hover:text-red-700">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Section Content (Collapsible) -->
                <div x-show="section.expanded" 
                     x-transition:enter="transition ease-out duration-200"
                     x-transition:enter-start="opacity-0 transform scale-95"
                     x-transition:enter-end="opacity-100 transform scale-100"
                     class="section-content border-t border-gray-200 p-4">
                    
                    <!-- Questions List -->
                    <div class="questions-list space-y-2" 
                         :data-section-id="section.id"
                         x-ref="'questionsList' + section.id">
                        <template x-for="question in section.questions" :key="question.id">
                            <div class="question-item bg-gray-50 p-3 rounded border border-gray-200 flex items-center justify-between"
                                 :data-question-id="question.id">
                                <div class="flex items-center space-x-3">
                                    <i class="fas fa-grip-vertical text-gray-400 cursor-move"></i>
                                    <div>
                                        <p class="font-medium" x-text="question.label"></p>
                                        <span class="text-xs text-gray-500" x-text="question.type_display"></span>
                                    </div>
                                </div>
                                <div class="flex items-center space-x-2">
                                    <a :href="'/admin/question/' + question.id + '/edit/'" 
                                       class="text-blue-500 hover:text-blue-700">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <button @click="deleteQuestion(question.id)" 
                                            class="text-red-500 hover:text-red-700">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </template>
                    </div>
                    
                    <!-- Add Question Button -->
                    <button @click="addQuestion(section.id)" 
                            data-te-toggle="modal" 
                            data-te-target="#addQuestion"
                            class="mt-3 w-full border-2 border-dashed border-gray-300 rounded-lg p-3 text-gray-500 hover:border-blue-500 hover:text-blue-500 transition">
                        <i class="fas fa-plus"></i> Add Question
                    </button>
                </div>
            </div>
        </template>
    </div>
    
    <!-- Unassigned Questions Area -->
    <div class="unassigned-questions mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
        <h3 class="text-lg font-semibold mb-3">
            <i class="fas fa-exclamation-triangle text-yellow-600"></i>
            Unassigned Questions
            <span class="badge bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-sm ml-2"
                  x-text="unassignedQuestions.length"></span>
        </h3>
        <div class="questions-list space-y-2" data-section-id="unassigned" x-ref="unassignedList">
            <template x-for="question in unassignedQuestions" :key="question.id">
                <div class="question-item bg-white p-3 rounded border border-yellow-300 flex items-center justify-between"
                     :data-question-id="question.id">
                    <div class="flex items-center space-x-3">
                        <i class="fas fa-grip-vertical text-gray-400 cursor-move"></i>
                        <p class="font-medium" x-text="question.label"></p>
                    </div>
                    <a :href="'/admin/question/' + question.id + '/edit/'" 
                       class="text-blue-500 hover:text-blue-700">
                        <i class="fas fa-edit"></i>
                    </a>
                </div>
            </template>
            <p x-show="unassignedQuestions.length === 0" class="text-gray-500 text-center py-4">
                No unassigned questions
            </p>
        </div>
    </div>
    
    <!-- Add Section Button -->
    <button @click="addSection()" 
            class="mt-6 w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition">
        <i class="fas fa-plus"></i> Add Section
    </button>
</div>

<script>
function sectionManager() {
    return {
        sections: [],
        unassignedQuestions: [],
        surveySlug: document.querySelector('[data-survey-slug]').dataset.surveySlug,
        
        async init() {
            // Load sections and questions
            await this.loadData();
            
            // Initialize Sortable for sections
            new Sortable(this.$refs.sectionsContainer, {
                handle: '.drag-handle',
                animation: 150,
                ghostClass: 'opacity-50',
                onEnd: (evt) => {
                    this.reorderSections(evt.oldIndex, evt.newIndex);
                }
            });
            
            // Initialize Sortable for each section's questions
            this.$nextTick(() => {
                this.sections.forEach(section => {
                    const listEl = this.$refs['questionsList' + section.id];
                    if (listEl) {
                        new Sortable(listEl, {
                            group: 'questions',
                            animation: 150,
                            ghostClass: 'opacity-50',
                            onEnd: (evt) => {
                                this.moveQuestion(evt.item.dataset.questionId, 
                                                evt.to.dataset.sectionId,
                                                evt.newIndex);
                            }
                        });
                    }
                });
                
                // Unassigned questions sortable
                if (this.$refs.unassignedList) {
                    new Sortable(this.$refs.unassignedList, {
                        group: 'questions',
                        animation: 150,
                        ghostClass: 'opacity-50',
                        onEnd: (evt) => {
                            this.moveQuestion(evt.item.dataset.questionId, null, evt.newIndex);
                        }
                    });
                }
            });
        },
        
        async loadData() {
            const response = await fetch(`/api/survey/${this.surveySlug}/sections/`);
            const data = await response.json();
            this.sections = data.sections.map(s => ({...s, expanded: false, editing: false}));
            this.unassignedQuestions = data.unassigned_questions || [];
        },
        
        toggleSection(sectionId) {
            const section = this.sections.find(s => s.id === sectionId);
            if (section && !section.editing) {
                section.expanded = !section.expanded;
            }
        },
        
        startEditSection(sectionId) {
            const section = this.sections.find(s => s.id === sectionId);
            if (section) {
                section.editing = true;
                this.$nextTick(() => {
                    section.originalName = section.name;
                    section.originalDescription = section.description;
                });
            }
        },
        
        async saveSection(section) {
            section.editing = false;
            const response = await fetch(`/api/section/${section.id}/update/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    name: section.name,
                    description: section.description
                })
            });
            
            if (!response.ok) {
                alert('Failed to save section');
                section.name = section.originalName;
                section.description = section.originalDescription;
            }
        },
        
        cancelEdit(section) {
            section.editing = false;
            section.name = section.originalName;
            section.description = section.originalDescription;
        },
        
        async addSection() {
            const response = await fetch('/api/section/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    survey_slug: this.surveySlug,
                    name: 'New Section',
                    ordering: this.sections.length
                })
            });
            
            if (response.ok) {
                const newSection = await response.json();
                this.sections.push({...newSection, expanded: true, editing: false, questions: []});
            }
        },
        
        async deleteSection(sectionId) {
            if (!confirm('Delete this section? Questions will become unassigned.')) return;
            
            const response = await fetch(`/api/section/${sectionId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (response.ok) {
                await this.loadData(); // Reload to get unassigned questions
            }
        },
        
        async reorderSections(oldIndex, newIndex) {
            const section = this.sections[oldIndex];
            this.sections.splice(oldIndex, 1);
            this.sections.splice(newIndex, 0, section);
            
            // Update ordering on backend
            await fetch('/api/sections/reorder/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    sections: this.sections.map((s, idx) => ({id: s.id, ordering: idx}))
                })
            });
        },
        
        async moveQuestion(questionId, targetSectionId, newIndex) {
            const response = await fetch(`/api/question/${questionId}/move/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    section_id: targetSectionId,
                    ordering: newIndex
                })
            });
            
            if (response.ok) {
                await this.loadData(); // Reload to update UI
            }
        },
        
        addQuestion(sectionId) {
            // Store section ID for modal context
            sessionStorage.setItem('currentSectionId', sectionId);
        },
        
        async deleteQuestion(questionId) {
            if (!confirm('Delete this question?')) return;
            
            const response = await fetch(`/api/question/${questionId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (response.ok) {
                await this.loadData();
            }
        },
        
        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        }
    }
}
</script>
```

**Rationale**:
- All functionality in one component for simplicity
- Alpine.js handles reactivity without complex state management
- Sortable.js handles all drag-and-drop complexity
- Server-side rendering for initial load, AJAX for updates
- Unassigned questions area provides safety net for orphaned questions

**Alternatives Considered**:
- Separate components: More modular but increases complexity
- Real-time updates: Unnecessary for single-user admin workflow
- Undo/redo: Complex to implement, low value for this use case

### 4. File Upload Configuration Panel

**Decision**: Modal-based configuration with live preview

**Component**:
```html
<!-- File Upload Config Component (shown when type_field === 10) -->
<div x-data="fileUploadConfig()" class="file-upload-config mt-4 p-4 bg-blue-50 rounded-lg">
    <h4 class="font-semibold mb-3">File Upload Settings</h4>
    
    <!-- Allowed File Types -->
    <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Allowed File Types:</label>
        <div class="grid grid-cols-2 gap-2">
            <label class="flex items-center space-x-2">
                <input type="checkbox" value="pdf" x-model="allowedTypes" class="rounded">
                <span>PDF Documents</span>
            </label>
            <label class="flex items-center space-x-2">
                <input type="checkbox" value="doc" x-model="allowedTypes" class="rounded">
                <span>Word Documents</span>
            </label>
            <label class="flex items-center space-x-2">
                <input type="checkbox" value="image" x-model="allowedTypes" class="rounded">
                <span>Images (JPG, PNG)</span>
            </label>
            <label class="flex items-center space-x-2">
                <input type="checkbox" value="excel" x-model="allowedTypes" class="rounded">
                <span>Excel Spreadsheets</span>
            </label>
        </div>
        <div class="mt-2">
            <label class="flex items-center space-x-2">
                <input type="checkbox" value="other" x-model="allowedTypes" class="rounded">
                <span>Other:</span>
                <input type="text" x-model="customTypes" 
                       placeholder=".txt, .csv"
                       class="px-2 py-1 border rounded text-sm"
                       x-show="allowedTypes.includes('other')">
            </label>
        </div>
    </div>
    
    <!-- Max File Size -->
    <div class="mb-4">
        <label class="block text-sm font-medium mb-2">
            Max File Size: <span x-text="maxSize"></span> MB
        </label>
        <input type="range" x-model="maxSize" min="1" max="50" step="1" 
               class="w-full">
    </div>
    
    <!-- Multiple Files -->
    <div class="mb-4">
        <label class="flex items-center space-x-2">
            <input type="checkbox" x-model="allowMultiple" class="rounded">
            <span>Allow Multiple Files</span>
        </label>
        <div x-show="allowMultiple" class="mt-2 ml-6">
            <label class="block text-sm">
                Max Files:
                <input type="number" x-model="maxFiles" min="1" max="10" 
                       class="px-2 py-1 border rounded w-20">
            </label>
        </div>
    </div>
    
    <!-- Live Preview -->
    <div class="mt-6 p-4 bg-white border-2 border-gray-300 rounded">
        <h5 class="font-medium mb-2">Preview:</h5>
        <label class="block mb-1 font-medium" x-text="'Upload your file'"></label>
        <input type="file" 
               :accept="getAcceptAttribute()"
               :multiple="allowMultiple"
               class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
        <small class="text-gray-600 mt-1 block" x-text="getHelpText()"></small>
    </div>
    
    <!-- Hidden input to store config -->
    <input type="hidden" name="file_config" :value="JSON.stringify(getConfig())">
</div>

<script>
function fileUploadConfig() {
    return {
        allowedTypes: ['pdf', 'doc'],
        customTypes: '',
        maxSize: 5,
        allowMultiple: false,
        maxFiles: 3,
        
        getAcceptAttribute() {
            const typeMap = {
                'pdf': '.pdf',
                'doc': '.doc,.docx',
                'image': 'image/jpeg,image/png,image/gif',
                'excel': '.xls,.xlsx'
            };
            
            let accept = this.allowedTypes
                .filter(t => t !== 'other')
                .map(t => typeMap[t])
                .filter(Boolean)
                .join(',');
            
            if (this.allowedTypes.includes('other') && this.customTypes) {
                accept += ',' + this.customTypes;
            }
            
            return accept;
        },
        
        getHelpText() {
            const typeLabels = {
                'pdf': 'PDF',
                'doc': 'DOC/DOCX',
                'image': 'Images',
                'excel': 'Excel'
            };
            
            const types = this.allowedTypes
                .filter(t => t !== 'other')
                .map(t => typeLabels[t])
                .join(', ');
            
            let text = `Accepted: ${types}`;
            if (this.allowedTypes.includes('other') && this.customTypes) {
                text += ', ' + this.customTypes;
            }
            text += ` (Max ${this.maxSize}MB`;
            
            if (this.allowMultiple) {
                text += `, up to ${this.maxFiles} files`;
            }
            text += ')';
            
            return text;
        },
        
        getConfig() {
            return {
                allowed_types: this.allowedTypes,
                custom_types: this.customTypes,
                max_size: this.maxSize * 1024 * 1024,
                allow_multiple: this.allowMultiple,
                max_files: this.maxFiles
            };
        }
    }
}
</script>
```

**Storage Strategy**:
Store configuration in Question.help_text as JSON (backward compatible) or add metadata JSONField in future migration.

**Rationale**:
- Live preview provides immediate feedback
- Configuration stored with question for validation
- Simple checkbox interface for common types
- Extensible for custom file types

### 5. API Endpoints

**New REST-style endpoints**:

```python
# djf_surveys/admins/api_views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from djf_surveys.models import Survey, Section, Question
import json

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SurveySectionsAPIView(View):
    """Get all sections and questions for a survey"""
    
    def get(self, request, slug):
        survey = Survey.objects.get(slug=slug)
        sections = Section.objects.filter(survey=survey).prefetch_related('questions').order_by('ordering')
        unassigned = Question.objects.filter(survey=survey, section__isnull=True)
        
        return JsonResponse({
            'survey': {
                'id': survey.id,
                'name': survey.name,
                'slug': survey.slug
            },
            'sections': [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'ordering': s.ordering,
                    'questions': [
                        {
                            'id': q.id,
                            'label': q.label,
                            'type_field': q.type_field,
                            'type_display': q.get_type_field_display(),
                            'ordering': q.ordering,
                            'required': q.required
                        }
                        for q in s.questions.all().order_by('ordering')
                    ]
                }
                for s in sections
            ],
            'unassigned_questions': [
                {
                    'id': q.id,
                    'label': q.label,
                    'type_field': q.type_field,
                    'type_display': q.get_type_field_display()
                }
                for q in unassigned
            ]
        })

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionCreateAPIView(View):
    """Create new section"""
    
    def post(self, request):
        data = json.loads(request.body)
        survey = Survey.objects.get(slug=data['survey_slug'])
        
        section = Section.objects.create(
            survey=survey,
            name=data.get('name', 'New Section'),
            description=data.get('description', ''),
            ordering=data.get('ordering', 0)
        )
        
        return JsonResponse({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'ordering': section.ordering,
            'questions': []
        })

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionUpdateAPIView(View):
    """Update section"""
    
    def patch(self, request, pk):
        data = json.loads(request.body)
        section = Section.objects.get(pk=pk)
        
        if 'name' in data:
            section.name = data['name']
        if 'description' in data:
            section.description = data['description']
        
        section.save()
        
        return JsonResponse({'status': 'success'})

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionDeleteAPIView(View):
    """Delete section (questions become unassigned)"""
    
    def delete(self, request, pk):
        section = Section.objects.get(pk=pk)
        # Questions automatically become unassigned (section set to null)
        section.delete()
        return JsonResponse({'status': 'success'})

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionsReorderAPIView(View):
    """Bulk reorder sections"""
    
    def post(self, request):
        data = json.loads(request.body)
        
        for item in data['sections']:
            Section.objects.filter(pk=item['id']).update(ordering=item['ordering'])
        
        return JsonResponse({'status': 'success'})

@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class QuestionMoveAPIView(View):
    """Move question to different section"""
    
    def post(self, request, pk):
        data = json.loads(request.body)
        question = Question.objects.get(pk=pk)
        
        # Update section (null for unassigned)
        section_id = data.get('section_id')
        question.section = Section.objects.get(pk=section_id) if section_id else None
        question.ordering = data.get('ordering', 0)
        question.save()
        
        # Reorder other questions in target section
        if section_id:
            questions = Question.objects.filter(section_id=section_id).order_by('ordering')
            for idx, q in enumerate(questions):
                if q.ordering != idx:
                    q.ordering = idx
                    q.save()
        
        return JsonResponse({'status': 'success'})
```

**URL Configuration**:
```python
# djf_surveys/admins/urls.py

urlpatterns = [
    # ... existing patterns ...
    
    # New API endpoints
    path('api/survey/<slug:slug>/sections/', SurveySectionsAPIView.as_view(), name='api-survey-sections'),
    path('api/section/create/', SectionCreateAPIView.as_view(), name='api-section-create'),
    path('api/section/<int:pk>/update/', SectionUpdateAPIView.as_view(), name='api-section-update'),
    path('api/section/<int:pk>/delete/', SectionDeleteAPIView.as_view(), name='api-section-delete'),
    path('api/sections/reorder/', SectionsReorderAPIView.as_view(), name='api-sections-reorder'),
    path('api/question/<int:pk>/move/', QuestionMoveAPIView.as_view(), name='api-question-move'),
]
```

**Security**:
- All endpoints require `@staff_member_required`
- CSRF protection on all mutating operations
- Input validation for all fields
- Permission checks ensure user can modify survey

**Alternatives Considered**:
- Django REST Framework: Overkill for simple CRUD, adds dependency
- GraphQL: Too complex for this use case
- WebSockets: No need for real-time updates

## Risks / Trade-offs

### Risks

1. **JavaScript Dependency**
   - Risk: Users with JS disabled cannot use enhanced features
   - Mitigation: Progressive enhancement - basic forms still work
   - Fallback: Keep legacy admin interface available via setting

2. **Browser Compatibility**
   - Risk: Older browsers may not support Alpine.js/Sortable.js
   - Mitigation: Test on IE11, Edge, Chrome, Firefox, Safari
   - Document minimum browser requirements

3. **Performance with Large Surveys**
   - Risk: Surveys with 50+ sections may slow down
   - Mitigation: Lazy load section content, pagination, virtual scrolling
   - Monitor: Add performance metrics

4. **Data Loss During Drag**
   - Risk: Network error during drag-and-drop could lose changes
   - Mitigation: Optimistic UI updates with rollback on error
   - Add: "Saving..." indicators and error messages

### Trade-offs

- **Complexity vs Features**: Adding JavaScript increases complexity but significantly improves UX
- **Development Time**: ~2-3 weeks for full implementation vs immediate value
- **Maintenance**: More frontend code to maintain but cleaner separation of concerns
- **Learning Curve**: Admins need brief training but interface is intuitive

## Migration Plan

### Phase 1: Foundation (Week 1)
1. Add file upload to modal (1 day)
2. Test file upload creation (1 day)
3. Create API endpoints (2 days)
4. Unit tests for APIs (1 day)

### Phase 2: Section Manager (Week 2)
1. Build section component HTML/CSS (2 days)
2. Integrate Alpine.js and Sortable.js (1 day)
3. Connect to API endpoints (1 day)
4. Test drag-and-drop (1 day)

### Phase 3: Question Management (Week 3)
1. Add question drag-and-drop (2 days)
2. Unassigned questions area (1 day)
3. File config panel (1 day)
4. Integration testing (1 day)

### Phase 4: Polish & Deploy (Week 4)
1. Accessibility improvements (1 day)
2. Mobile responsiveness (1 day)
3. Documentation (1 day)
4. Staging deployment and UAT (2 days)

### Rollback Plan
- Feature flag: `ENHANCED_SURVEY_BUILDER = True` in settings
- Keep old templates as `*_legacy.html`
- Database changes: None required (backward compatible)
- Quick disable: Set feature flag to False

## Open Questions

1. **File storage location for config**: Store in help_text (current) or add metadata JSONField (future)?
   - **Decision**: Use help_text initially, migrate to metadata field in future if needed

2. **Mobile admin interface**: Should we disable drag-and-drop on mobile or provide alternative?
   - **Decision**: Disable drag, add up/down arrow buttons for mobile

3. **Undo/Redo**: Worth implementing for section/question operations?
   - **Decision**: Not in MVP, consider in Phase 2 based on feedback

4. **Real-time collaboration**: Multiple admins editing same survey?
   - **Decision**: Out of scope, use Django's optimistic locking (last write wins)

5. **Visual flow builder**: Include in MVP or defer to Phase 2?
   - **Decision**: Optional Phase 2 feature, core functionality is more important

## Conclusion

This design provides a comprehensive, implementable solution for enhancing the multi-session survey builder UI. Key strengths:

- **Minimal dependencies**: Alpine.js + Sortable.js only
- **Progressive enhancement**: Works without JavaScript
- **Backward compatible**: No breaking changes
- **Modern UX**: Drag-and-drop, collapsible sections, live previews
- **Secure**: Staff-only access, CSRF protection, input validation
- **Maintainable**: Clear separation of concerns, well-documented APIs

The design prioritizes pragmatism over perfection, delivering significant value with reasonable complexity.
