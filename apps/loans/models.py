from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.books.models import Book

class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.book.available_copies -= 1
            self.book.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.returned:
            self.book.available_copies += 1
            self.book.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.book.title}"