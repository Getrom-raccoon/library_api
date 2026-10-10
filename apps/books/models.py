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


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    genre = models.CharField(max_length=50, blank=True, null=True)
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