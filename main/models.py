from djongo import models
from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)  # required field

    def __str__(self):
        return self.name

from django.utils import timezone

class Order(models.Model):
    session_id = models.CharField(max_length=100)
    items = models.JSONField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
