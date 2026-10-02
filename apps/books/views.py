from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'reading_status', 'rating', 'author']
    search_fields = ['title', 'author__name', 'isbn']
    ordering_fields = ['title', 'published_year', 'rating', 'added_at']

    def get_queryset(self):
        # Пользователь видит только свои книги
        return Book.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Автоматически назначаем владельца
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по книгам текущего пользователя"""
        user_books = self.get_queryset()

        total = user_books.count()
        finished = user_books.filter(reading_status='finished').count()
        in_progress = user_books.filter(reading_status='in_progress').count()
        not_started = user_books.filter(reading_status='not_started').count()
        abandoned = user_books.filter(reading_status='abandoned').count()

        avg_rating = user_books.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']

        return Response({
            'total': total,
            'finished': finished,
            'in_progress': in_progress,
            'not_started': not_started,
            'abandoned': abandoned,
            'avg_rating': avg_rating,
        })


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return Author.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)