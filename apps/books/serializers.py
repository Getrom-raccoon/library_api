from rest_framework import serializers
from .models import Book, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'

    def validate(self, data):
        total = data.get('total_copies', 0)
        available = data.get('available_copies', 0)
        if total < 0:
            raise serializers.ValidationError({'total_copies': 'Общее количество не может быть отрицательным'})
        if available < 0:
            raise serializers.ValidationError({'available_copies': 'Доступных копий не может быть меньше 0'})
        if available > total:
            raise serializers.ValidationError({'available_copies': 'Доступных копий не может быть больше общего количества'})
        return data