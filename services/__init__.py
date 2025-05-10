"""
Services initialization module for Monetize-blogs application.
This module imports all service singletons for easy access.
"""
from .blog_service import blog_service
from .seo_service import seo_service
from .image_service import image_service
from .social_service import social_service
from .trend_service import trend_service
from .automation_service import automation_service
from .analytics_service import analytics_service
from .ad_service import ad_service

__all__ = [
    'blog_service',
    'seo_service',
    'image_service',    'social_service',
    'trend_service',
    'automation_service',
    'analytics_service',
    'ad_service'
]
