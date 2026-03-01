from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    ]

    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="users",
        blank=True,
        null=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["role"]),
        ]
