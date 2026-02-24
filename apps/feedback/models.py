from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "feedback"
        indexes = [
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"Feedback for Order {self.order_id} - {self.rating}/5"