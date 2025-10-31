import os
import mimetypes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class FileTypeValidator:
    """Validate file type by extension and MIME type."""
    def __init__(self, allowed_types=None):
        self.allowed_types = allowed_types or settings.SURVEY_FILE_ALLOWED_TYPES
    
    def __call__(self, file):
        from django.utils.translation import gettext as translate
        # Get file extension
        ext = os.path.splitext(file.name)[1][1:].lower()
        
        if ext not in self.allowed_types:
            raise ValidationError(
                translate('File type not allowed. Allowed types: %(types)s') % {
                    'types': ', '.join(self.allowed_types)
                }
            )
        
        # Verify MIME type matches extension
        mime_type, mime_encoding = mimetypes.guess_type(file.name)
        if mime_type:
            # Basic MIME type validation
            expected_mime_types = {
                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 
                'gif': 'image/gif', 'pdf': 'application/pdf',
                'doc': 'application/msword', 
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            expected = expected_mime_types.get(ext)
            if expected and mime_type != expected:
                raise ValidationError(translate('File content does not match file extension.'))


class FileSizeValidator:
    """Validate file size."""
    def __init__(self, max_size=None):
        self.max_size = max_size or settings.SURVEY_FILE_UPLOAD_MAX_SIZE
    
    def __call__(self, file):
        if file.size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            raise ValidationError(
                _('File too large. Maximum size: %(max)s MB') % {'max': max_mb}
            )


class RatingValidator(object):
    def __init__(self, max):
        self.max = max

    def __call__(self, value):
        try:
            rating = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _('%s is not a number.' % value)
            )

        if rating > self.max:
            raise ValidationError(
                _('Qiymat ruxsat etilgan reytinglarning eng ko‘p miqdoridan oshib ketmasligi lozim.')
            )

        if rating < 1:
            raise ValidationError(
                _('Qiymat 1 dan kam bo‘lmasligi kerak.')
            )


