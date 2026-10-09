from django.db.models import Q
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


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