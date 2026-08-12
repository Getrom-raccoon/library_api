from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'author', 'published_year']
    search_fields = ['title', 'author__name', 'isbn']
    ordering_fields = ['title', 'published_year']

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']