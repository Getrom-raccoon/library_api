from django.contrib import admin
from .models import Book, Author, Work, ISBNCache, Series


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
    list_display = (
        'id', 'title', 'author', 'publisher',
        'series', 'series_number',
        'isbn', 'available_copies', 'reading_status',
    )
    list_filter = ('author', 'reading_status', 'publisher', 'series')
    search_fields = ('title', 'isbn', 'author__name', 'publisher', 'series__name')
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


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'books_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('owner',)
    readonly_fields = ('created_at', 'updated_at')

    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Книг в серии'