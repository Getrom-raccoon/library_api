from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, SeriesViewSet, QuoteViewSet, ReadingSessionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'series', SeriesViewSet, basename='series')
router.register(r'quotes', QuoteViewSet, basename='quotes')
router.register('reading-sessions', ReadingSessionViewSet, basename='reading-sessions')

urlpatterns = [
    path('', include(router.urls)),
]