from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'loan_date', 'due_date', 'returned')
    list_filter = ('returned', 'loan_date')
    search_fields = ('user__email', 'book__title')