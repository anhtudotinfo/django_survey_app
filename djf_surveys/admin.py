from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    Survey, Question, Question2, Answer, Answer2, 
    UserAnswer, UserAnswer2, Direction, UserRating,
    Section, BranchRule, DraftResponse
)


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class BranchRuleInline(admin.TabularInline):
    model = BranchRule
    fk_name = 'section'  # Specify which FK to use for the inline
    extra = 0
    fields = ('condition_question', 'condition_operator', 'condition_value', 'next_section', 'priority')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "condition_question":
            # Only show questions from current survey's sections
            if request._obj_:
                kwargs["queryset"] = Question.objects.filter(survey=request._obj_.survey)
        if db_field.name == "next_section":
            # Only show sections from same survey
            if request._obj_:
                kwargs["queryset"] = Section.objects.filter(survey=request._obj_.survey)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'survey', 'ordering', 'question_count')
    list_filter = ('survey',)
    search_fields = ('name', 'survey__name')
    inlines = [BranchRuleInline]
    
    def get_form(self, request, obj=None, **kwargs):
        # Store the object in the request for use in inline formfield_for_foreignkey
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'
    
    def delete_model(self, request, obj):
        # Prevent deletion if section has questions
        if obj.questions.exists():
            from django.contrib import messages
            messages.error(request, f'Cannot delete section "{obj.name}" because it contains {obj.questions.count()} questions. Please reassign or delete questions first.')
            return
        super().delete_model(request, obj)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Check for circular references after save
        from django.contrib import messages
        cycles = BranchRule.detect_circular_references(obj.survey)
        if cycles:
            messages.warning(
                request,
                f'Warning: Circular references detected in branch rules. This may cause infinite loops.'
            )


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ('name', 'description', 'ordering')
    show_change_link = True


class AdminQuestion(admin.ModelAdmin):
    list_display = ('survey', 'section', 'label', 'type_field', 'help_text', 'required', 'ordering')
    list_filter = ('survey', 'section', 'type_field')
    search_fields = ('survey__name', 'label')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "section":
            # Filter sections by survey if available
            survey_id = request.GET.get('survey')
            if survey_id:
                kwargs["queryset"] = Section.objects.filter(survey_id=survey_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AdminQuestion2(admin.ModelAdmin):
    list_display = ('survey', 'label', 'type_field', 'help_text', 'required')
    search_fields = ('survey__name', )


class AdminAnswer(admin.ModelAdmin):
    list_display = ('question', 'get_label', 'value', 'user_answer')
    search_fields = ('question__label', 'value',)
    list_filter = ('user_answer', 'created_at')

    def get_label(self, obj):
        return obj.question.label
    get_label.admin_order_field = 'question'
    get_label.short_description = 'Label'


class AdminAnswer2(admin.ModelAdmin):
    list_display = ('question', 'value', 'user_rating', 'created_at')
    search_fields = ('question__label', 'value')
    list_filter = ('user_rating', 'created_at')


class AdminUserAnswer(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created_at', 'updated_at')


class AdminUserAnswer2(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created_at', 'updated_at')
    search_fields = ('survey__name', 'user__username')


class AdminUserRating(admin.ModelAdmin):
    list_display = ('user_answer', 'rated_user', 'created_at')
    search_fields = ('user_answer__user__username', 'rated_user__username')


class AdminSurvey(admin.ModelAdmin):
    list_display = ('name', 'slug', 'can_anonymous_user', 'duplicate_entry', 'private_response', 'section_count')
    list_filter = ('can_anonymous_user', 'duplicate_entry', 'private_response', 'editable', 'deletable')
    exclude = ['slug']
    inlines = [SectionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('can_anonymous_user', 'duplicate_entry', 'private_response', 'editable', 'deletable')
        }),
        ('Notifications', {
            'fields': ('notification_to', 'success_page_content'),
            'classes': ('collapse',)
        }),
    )
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'


@admin.register(DraftResponse)
class DraftResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'user', 'session_key_short', 'current_section', 'expires_at', 'updated_at')
    list_filter = ('survey', 'expires_at')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'data')
    
    def session_key_short(self, obj):
        if obj.session_key:
            return obj.session_key[:8] + '...'
        return '-'
    session_key_short.short_description = 'Session'


@admin.register(BranchRule)
class BranchRuleAdmin(admin.ModelAdmin):
    list_display = ('section', 'condition_question', 'condition_operator', 'condition_value', 'next_section', 'priority')
    list_filter = ('section__survey', 'condition_operator')
    search_fields = ('section__name', 'condition_question__label')
    ordering = ('section', 'priority')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "condition_question":
            # Filter by survey if section is selected
            section_id = request.GET.get('section')
            if section_id:
                try:
                    section = Section.objects.get(id=section_id)
                    kwargs["queryset"] = Question.objects.filter(survey=section.survey)
                except Section.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Customize Admin Site
admin.site.site_header = "Survey Management System"
admin.site.site_title = "Survey Admin"
admin.site.index_title = "Welcome to Survey Administration"

# Register models
admin.site.register(Survey, AdminSurvey)
admin.site.register(Question, AdminQuestion)
admin.site.register(Question2, AdminQuestion2)
admin.site.register(Answer, AdminAnswer)
admin.site.register(Answer2, AdminAnswer2)
admin.site.register(UserAnswer, AdminUserAnswer)
admin.site.register(UserAnswer2, AdminUserAnswer2)
admin.site.register(UserRating, AdminUserRating)
