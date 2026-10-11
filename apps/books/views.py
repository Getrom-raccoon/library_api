from django.db.models import Q
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Author, ISBNCache
from .serializers import BookSerializer, AuthorSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .isbn_lookup import lookup_wb, lookup_openlibrary


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['genre', 'reading_status', 'rating', 'author']
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
                if (b.title and search_lower in b.title.lower()) \
                        or (b.author and b.author.name
                            and search_lower in b.author.name.lower()) \
                        or (b.isbn and search_lower in b.isbn.lower()):
                    matching_ids.append(b.id)
            queryset = Book.objects.filter(id__in=matching_ids).select_related('author')

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='lookup-isbn')
    def lookup_isbn(self, request):
        isbn = (request.query_params.get('isbn') or '').strip()
        # Убираем дефисы, пробелы
        isbn = re.sub(r'[^0-9Xx]', '', isbn)

        if not isbn or len(isbn) < 10:
            return Response(
                {'error': 'Введите корректный ISBN (10 или 13 цифр)'},
                status=400,
            )

        # 1. Проверяем кэш
        cached = ISBNCache.objects.filter(isbn=isbn).first()
        if cached and (timezone.now() - cached.updated_at) < timedelta(days=30):
            return Response({
                'success': True,
                'from_cache': True,
                **self._serialize_isbn(cached),
            })

        # 2. WB
        data = lookup_wb(isbn)

        # 3. Если не нашли — Open Library
        if not data:
            data = lookup_openlibrary(isbn)

        if not data:
            return Response(
                {'error': 'Книга не найдена ни в Wildberries, ни в Open Library'},
                status=404,
            )

        # 4. Сохраняем/обновляем в кэш
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
            raise ValidationError({'name': 'Автор с таким именем уже существует'})
        serializer.save(owner=self.request.user)