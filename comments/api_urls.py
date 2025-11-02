from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PageViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'pages', PageViewSet, basename='page')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]