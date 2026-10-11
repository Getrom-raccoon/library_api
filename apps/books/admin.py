from django.contrib import admin
from .models import Book, Author, Work, ISBNCache


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner')
    search_fields = ('name',)
    list_filter = ('owner',)


class WorkInline(admin.TabularInline):
    """Произведения, редактируются прямо на странице книги."""
    model = Work
    extra = 1
    fields = ('order', 'title', 'author', 'is_read')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'genre', 'isbn', 'available_copies', 'reading_status')
    list_filter = ('genre', 'author', 'reading_status')
    search_fields = ('title', 'isbn', 'author__name')
    inlines = [WorkInline]


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'book', 'is_read', 'order')
    list_filter = ('is_read',)
    search_fields = ('title', 'author', 'book__title')
    ordering = ('book', 'order')

@admin.register(ISBNCache)
class ISBNCacheAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author_name', 'source', 'updated_at')
    search_fields = ('isbn', 'title', 'author_name')
    list_filter = ('source',)
    readonly_fields = ('created_at', 'updated_at')