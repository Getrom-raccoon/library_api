from rest_framework import serializers
from .models import Book, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)
    reading_status_display = serializers.CharField(
        source='get_reading_status_display',
        read_only=True
    )

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_detail',
            'genre', 'isbn', 'published_year',
            'total_copies', 'available_copies',
            'owner', 'reading_status', 'reading_status_display',
            'rating', 'notes', 'pages',
            'started_reading', 'finished_reading',
            'added_at'
        ]
        read_only_fields = ['owner', 'added_at']

    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value