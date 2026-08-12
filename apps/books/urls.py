from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', include(router.urls)),
]