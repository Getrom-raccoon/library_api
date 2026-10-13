import re

from rest_framework import serializers
from .models import Book, Author, Work, ISBNCache, Series


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['id', 'title', 'author', 'is_read', 'order']
        read_only_fields = ['id']


class SeriesSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'name', 'description', 'books_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_books_count(self, obj):
        return obj.books.count()


class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)
    series_detail = SeriesSerializer(source='series', read_only=True)
    reading_status_display = serializers.CharField(
        source='get_reading_status_display',
        read_only=True
    )
    works = WorkSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_detail',
            'genres', 'publisher',
            'series', 'series_detail', 'series_number',
            'isbn', 'published_year',
            'total_copies', 'available_copies',
            'owner', 'reading_status', 'reading_status_display',
            'rating', 'notes', 'pages', 'current_page',
            'started_reading', 'finished_reading',
            'added_at',
            'works',
        ]
        read_only_fields = ['owner', 'added_at']

    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value

    def validate_isbn(self, value):
        """Санитизация ISBN: убираем дефисы, пробелы, проверяем длину."""
        if value is None or value == '':
            return None
        cleaned = re.sub(r'[^0-9Xx]', '', str(value))
        if len(cleaned) < 10:
            raise serializers.ValidationError(
                'ISBN должен содержать не менее 10 цифр'
            )
        if len(cleaned) > 13:
            raise serializers.ValidationError(
                'ISBN не может быть длиннее 13 символов'
            )
        return cleaned

    def create(self, validated_data):
        works_data = validated_data.pop('works', [])
        book = Book.objects.create(**validated_data)
        for i, w in enumerate(works_data):
            w.pop('id', None)
            Work.objects.create(book=book, order=i, **w)
        return book

    def update(self, instance, validated_data):
        works_data = validated_data.pop('works', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if works_data is not None:
            instance.works.all().delete()
            for i, w in enumerate(works_data):
                w.pop('id', None)
                Work.objects.create(book=instance, order=i, **w)

        return instance