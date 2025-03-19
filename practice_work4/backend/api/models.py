from django.db import models
from django.contrib.auth.models import AbstractUser

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username
