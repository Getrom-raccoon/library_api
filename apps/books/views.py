import re

from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, Author, ISBNCache, Series
from .serializers import BookSerializer, AuthorSerializer, SeriesSerializer
from .isbn_lookup import lookup_openlibrary


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reading_status', 'rating', 'author']
    ordering_fields = ['title', 'published_year', 'rating', 'added_at']

    def get_queryset(self):
        queryset = Book.objects.filter(owner=self.request.user)

        search = self.request.query_params.get('search', '').strip()
        if search:
            # PostgreSQL с локалью C не понимает icontains для кириллицы.
            # Поэтому фильтруем в Python — регистронезависимо.
            search_lower = search.lower()
            matching_ids = []
            for b in queryset.select_related('author'):
                genres_match = any(
                    search_lower in (g or '').lower()
                    for g in (b.genres or [])
                )
                publisher_match = (
                    b.publisher and search_lower in b.publisher.lower()
                )
                if (b.title and search_lower in b.title.lower()) \
                        or (b.author and b.author.name
                            and search_lower in b.author.name.lower()) \
                        or (b.isbn and search_lower in b.isbn.lower()) \
                        or genres_match \
                        or publisher_match:
                    matching_ids.append(b.id)
            queryset = Book.objects.filter(id__in=matching_ids).select_related('author')

        # Фильтр по жанру (ищем в списке genres)
        genre = self.request.query_params.get('genre', '').strip()
        if genre:
            genre_lower = genre.lower()
            matching_ids = [
                b.id for b in queryset
                if any(genre_lower in (g or '').lower()
                       for g in (b.genres or []))
            ]
            queryset = queryset.filter(id__in=matching_ids)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='lookup-isbn')
    def lookup_isbn(self, request):
        """
        Поиск книги по ISBN через международный каталог.
        Сначала кэш (30 дней), потом Open Library.
        """
        raw = (request.query_params.get('isbn') or '').strip()
        isbn = re.sub(r'[^0-9Xx]', '', raw)

        if not isbn or len(isbn) < 10:
            return Response(
                {'error': 'Введите корректный ISBN (10 или 13 цифр)'},
                status=400,
            )

        # 1. Проверяем кэш — данные не старше 30 дней
        cached = ISBNCache.objects.filter(isbn=isbn).first()
        if cached and (timezone.now() - cached.updated_at) < timedelta(days=30):
            return Response({
                'success': True,
                'from_cache': True,
                **self._serialize_isbn(cached),
            })

        # 2. Open Library
        data = lookup_openlibrary(isbn)

        if not data:
            return Response(
                {'error': 'Книга не найдена в международном каталоге'},
                status=404,
            )

        # 3. Кэшируем результат
        obj, _ = ISBNCache.objects.update_or_create(
            isbn=isbn, defaults=data
        )

        return Response({
            'success': True,
            'from_cache': False,
            **self._serialize_isbn(obj),
        })

    @staticmethod
    def _serialize_isbn(obj):
        return {
            'isbn': obj.isbn,
            'title': obj.title,
            'author': obj.author_name,
            'genre': obj.genre,
            'year': obj.year,
            'pages': obj.pages,
            'cover_url': obj.cover_url,
            'source': obj.source,
        }


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Author.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name', '').strip()
        # Защита от дублей
        existing = Author.objects.filter(
            owner=self.request.user, name__iexact=name
        ).first()
        if existing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                {'name': 'Автор с таким именем уже существует'}
            )
        serializer.save(owner=self.request.user)

class SeriesViewSet(viewsets.ModelViewSet):
    serializer_class = SeriesSerializer

    def get_queryset(self):
        return Series.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name', '').strip()
        existing = Series.objects.filter(
            owner=self.request.user, name__iexact=name
        ).first()
        if existing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                {'name': 'Серия с таким названием уже существует'}
            )
        serializer.save(owner=self.request.user)