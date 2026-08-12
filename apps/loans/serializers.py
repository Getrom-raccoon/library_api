from rest_framework import serializers
from .models import Loan
from apps.books.serializers import BookSerializer

class LoanSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ('user', 'loan_date')