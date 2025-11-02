from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    Survey, Question, Question2, Answer, Answer2, 
    UserAnswer, UserAnswer2, Direction, UserRating,
    Section, BranchRule, DraftResponse, SiteConfig, SiteConfigChangeLog
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
    list_display = ('survey', 'user', 'ip_address', 'browser', 'device', 'created_at', 'updated_at')
    list_filter = ('survey', 'browser', 'device', 'created_at')
    search_fields = ('user__username', 'ip_address', 'browser')
    readonly_fields = ('ip_address', 'user_agent', 'browser', 'os', 'device')


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


class SiteConfigChangeLogInline(admin.TabularInline):
    """Inline display of change logs."""
    model = SiteConfigChangeLog
    extra = 0
    readonly_fields = ('action', 'changed_by', 'created_at', 'notes', 'ip_address')
    can_delete = False
    max_num = 10
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for Site Configuration.
    
    Features:
    - Organized fieldsets for easy navigation
    - Preview functionality
    - Change logging
    - Version management
    """
    
    list_display = ('site_name', 'version', 'is_active', 'updated_at', 'action_buttons')
    list_filter = ('is_active', 'enable_user_registration', 'enable_anonymous_surveys')
    search_fields = ('site_name', 'site_tagline', 'notes')
    readonly_fields = ('version', 'created_at', 'updated_at', 'preview_colors')
    inlines = [SiteConfigChangeLogInline]
    
    fieldsets = (
        ('🏢 Site Identity', {
            'fields': ('is_active', 'site_name', 'site_tagline', 'logo', 'favicon', 'version'),
            'description': 'Basic site information and branding'
        }),
        ('🎨 Colors & Theming', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'preview_colors'),
            'description': 'Customize site colors (use hex codes like #6366f1)'
        }),
        ('🏠 Homepage Content', {
            'fields': ('homepage_title', 'homepage_subtitle', 'homepage_banner', 'homepage_video_url'),
            'classes': ('collapse',)
        }),
        ('📄 Footer Configuration', {
            'fields': ('footer_text', 'footer_address', 'footer_phone', 'footer_email'),
            'classes': ('collapse',)
        }),
        ('🌐 Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('📝 Static Pages Content', {
            'fields': ('about_page_content', 'contact_page_content', 'terms_page_content', 'privacy_page_content'),
            'classes': ('collapse',),
            'description': 'Content for static pages (supports HTML)'
        }),
        ('⚙️ Feature Toggles', {
            'fields': ('enable_user_registration', 'enable_anonymous_surveys', 'show_survey_stats'),
            'classes': ('collapse',)
        }),
        ('🔍 SEO & Analytics', {
            'fields': ('meta_description', 'meta_keywords', 'google_analytics_id'),
            'classes': ('collapse',)
        }),
        ('📋 Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def preview_colors(self, obj):
        """Display color preview swatches."""
        if obj.pk:
            html = f'''
            <div style="display: flex; gap: 15px; margin-top: 10px;">
                <div>
                    <div style="width: 100px; height: 40px; background: {obj.primary_color}; border: 1px solid #ddd; border-radius: 4px;"></div>
                    <small>Primary</small>
                </div>
                <div>
                    <div style="width: 100px; height: 40px; background: {obj.secondary_color}; border: 1px solid #ddd; border-radius: 4px;"></div>
                    <small>Secondary</small>
                </div>
                <div>
                    <div style="width: 100px; height: 40px; background: {obj.accent_color}; border: 1px solid #ddd; border-radius: 4px;"></div>
                    <small>Accent</small>
                </div>
            </div>
            '''
            from django.utils.safestring import mark_safe
            return mark_safe(html)
        return "Save to preview colors"
    preview_colors.short_description = "Color Preview"
    
    def action_buttons(self, obj):
        """Display action buttons."""
        if obj.pk:
            html = f'''
            <div style="display: flex; gap: 5px;">
                <a href="/admin/djf_surveys/siteconfig/{obj.pk}/change/" 
                   style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">
                    ✏️ Edit
                </a>
            </div>
            '''
            from django.utils.safestring import mark_safe
            return mark_safe(html)
        return "-"
    action_buttons.short_description = "Actions"
    
    def get_readonly_fields(self, request, obj=None):
        """Make version readonly after creation."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('version',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Ensure only one config is active."""
        super().save_model(request, obj, form, change)
        
        # Store user in request for logging (via signal)
        if not hasattr(request, '_site_config_user'):
            request._site_config_user = request.user
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of active configuration."""
        if obj and obj.is_active:
            return False
        return super().has_delete_permission(request, obj)
    
    class Media:
        css = {
            'all': ('admin/css/siteconfig.css',)
        }
        js = ('admin/js/siteconfig.js',)


@admin.register(SiteConfigChangeLog)
class SiteConfigChangeLogAdmin(admin.ModelAdmin):
    """Admin for viewing change logs."""
    list_display = ('config', 'action', 'changed_by', 'created_at', 'ip_address')
    list_filter = ('action', 'created_at')
    search_fields = ('config__site_name', 'changed_by__username', 'notes')
    readonly_fields = ('config', 'changed_by', 'action', 'changes', 'notes', 'ip_address', 'created_at')
    
    def has_add_permission(self, request):
        """No manual creation of logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Logs should not be deleted."""
        return request.user.is_superuser  # Only superusers can delete logs


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
