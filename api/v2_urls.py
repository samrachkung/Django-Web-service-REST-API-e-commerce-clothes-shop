from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Placeholder for v2 API endpoints
router = DefaultRouter()

@api_view(['GET'])
def v2_root(request):
    return Response({
        'message': 'API v2 - Coming Soon',
        'info': 'This is a placeholder for API version 2'
    })

urlpatterns = [
    path('', v2_root, name='v2-root'),
    path('', include(router.urls)),
]