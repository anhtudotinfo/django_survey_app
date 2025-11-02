"""
Context processors for djf_surveys.

These functions inject variables into all templates automatically.
"""

from djf_surveys.models import SiteConfig


def surveys_context(request):
    """
    Legacy context processor for backward compatibility.
    
    Provides master template path for templates that use {% extends get_master_template %}.
    """
    return {
        'get_master_template': 'djf_surveys/master.html',
    }


def site_config(request):
    """
    Inject site configuration into all templates.
    
    Makes the active SiteConfig available as {{ site_config }} in templates.
    
    Usage in templates:
        {{ site_config.site_name }}
        {{ site_config.logo.url }}
        {{ site_config.primary_color }}
    
    Returns:
        dict: Context with site_config key
    """
    try:
        config = SiteConfig.get_active()
    except Exception:
        # Fallback if database not ready or no config exists
        config = None
    
    return {
        'site_config': config
    }
