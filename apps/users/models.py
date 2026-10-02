from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    email_code = models.CharField(max_length=6, blank=True, null=True)
    email_code_created = models.DateTimeField(blank=True, null=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_created = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email