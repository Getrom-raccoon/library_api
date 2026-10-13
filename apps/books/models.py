from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()  # ← переместили сюда, наверх


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        null=True,
        blank=True,
        verbose_name='Владелец'
    )

    def __str__(self):
        return self.name


class Series(models.Model):
    """Серия книг"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название серии'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание серии',
        help_text='Необязательное описание серии'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='series',
        null=True,
        blank=True,
        verbose_name='Владелец'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'
        ordering = ['name']
        # Один пользователь не может иметь две серии с одинаковым названием
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_series_per_owner'
            )
        ]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    # Список жанров (JSON-массив строк) — вместо одиночного genre
    genres = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Жанры'
    )
    publisher = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Издательство'
    )
    # Ссылка на серию (если книга входит в серию)
    series = models.ForeignKey(
        Series,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='Серия',
        help_text='Серия, к которой относится книга'
    )
    series_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Номер в серии',
        help_text='Порядковый номер книги в серии'
    )
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    published_year = models.IntegerField(blank=True, null=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books',
        null=True,
        blank=True,
        verbose_name='Владелец'
    )

    class ReadingStatus(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начата'
        IN_PROGRESS = 'in_progress', 'В процессе'
        FINISHED = 'finished', 'Прочитана'
        ABANDONED = 'abandoned', 'Отложена'
        WANT_TO_BUY = 'want_to_buy', 'Хочу купить'

    reading_status = models.CharField(
        max_length=20,
        choices=ReadingStatus.choices,
        default=ReadingStatus.NOT_STARTED,
        verbose_name='Статус чтения'
    )

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Оценка',
        help_text='Оценка от 1 до 5'
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Заметки'
    )

    pages = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Количество страниц'
    )

    current_page = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Текущая страница',
        help_text='На какой странице остановился пользователь'
    )

    started_reading = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата начала чтения'
    )

    finished_reading = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата окончания чтения'
    )

    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self):
        return self.title

class Work(models.Model):
    """Произведение внутри книги (рассказ, повесть, стих и т.д.)."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Книга'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название произведения'
    )
    author = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Автор произведения',
        help_text='Если отличается от автора книги'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Quote(models.Model):
    """Цитата из книги с указанием страницы."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='quotes',
        verbose_name='Книга'
    )
    text = models.TextField(
        verbose_name='Текст цитаты',
        help_text='Сама цитата'
    )
    page = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Страница',
        help_text='На какой странице в книге'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Цитата'
        verbose_name_plural = 'Цитаты'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.text[:50]}... (стр. {self.page})'


class ISBNCache(models.Model):
    """Кэш данных о книгах по ISBN. Общий для всех пользователей."""
    isbn = models.CharField(
        max_length=20, unique=True, db_index=True, verbose_name='ISBN'
    )
    title = models.CharField(max_length=300, blank=True, verbose_name='Название')
    author_name = models.CharField(
        max_length=200, blank=True, verbose_name='Автор'
    )
    genre = models.CharField(max_length=100, blank=True, verbose_name='Жанр')
    year = models.IntegerField(null=True, blank=True, verbose_name='Год')
    pages = models.IntegerField(null=True, blank=True, verbose_name='Страниц')
    cover_url = models.URLField(blank=True, null=True, verbose_name='Обложка')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    source = models.CharField(
        max_length=20, default='wb', verbose_name='Источник'
    )
    raw_data = models.JSONField(
        blank=True, null=True, verbose_name='Сырые данные'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кэш ISBN'
        verbose_name_plural = 'Кэш ISBN'

    def __str__(self):
        return f'{self.isbn} — {self.title}'