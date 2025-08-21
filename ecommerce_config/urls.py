# ecommerce_config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import DRF Spectacular views only if installed
try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView
    )
    spectacular_available = True
except ImportError:
    spectacular_available = False

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API URLs - This is the main API routing
    path('api/', include('api.urls')),
]

# Add API Documentation only if drf-spectacular is installed
if spectacular_available:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)