from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

    REQUIRED_FIELDS = []



class Category(models.Model):
    title = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Task(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({'✓' if self.is_completed else '✗'})"