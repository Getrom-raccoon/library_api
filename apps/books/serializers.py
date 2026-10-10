from rest_framework import serializers
from .models import Book, Author, Work


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['id', 'title', 'author', 'is_read', 'order']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)
    reading_status_display = serializers.CharField(
        source='get_reading_status_display',
        read_only=True
    )
    works = WorkSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_detail',
            'genre', 'isbn', 'published_year',
            'total_copies', 'available_copies',
            'owner', 'reading_status', 'reading_status_display',
            'rating', 'notes', 'pages',
            'started_reading', 'finished_reading',
            'added_at',
            'works',
        ]
        read_only_fields = ['owner', 'added_at']

    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value

    def create(self, validated_data):
        works_data = validated_data.pop('works', [])
        book = Book.objects.create(**validated_data)
        for i, w in enumerate(works_data):
            w.pop('id', None)   # id не передаём при создании
            Work.objects.create(book=book, order=i, **w)
        return book

    def update(self, instance, validated_data):
        works_data = validated_data.pop('works', None)

        # Обновляем скалярные поля книги
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Если works передали — пересоздаём их полностью
        if works_data is not None:
            instance.works.all().delete()
            for i, w in enumerate(works_data):
                w.pop('id', None)
                Work.objects.create(book=instance, order=i, **w)

        return instance