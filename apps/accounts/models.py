from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models.base import TimestampModel


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


class GuestUser(TimestampModel):
    """
    Represents an anonymous guest tied to a Django session.
    Enables guests to browse menus and place orders without authentication.
    This model is NOT part of Django's auth system.
    """

    session_key = models.CharField(max_length=40, unique=True)
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="guest_users",
    )

    class Meta:
        db_table = "guest_users"
        indexes = [
            models.Index(fields=["session_key"]),
        ]

    def __str__(self):
        return f"Guest({self.session_key[:8]}...) @ {self.restaurant.name}"
