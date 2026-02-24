from django.db import models


class Table(models.Model):
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="tables",
    )
    table_number = models.PositiveIntegerField()
    qr_code_string = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "tables"
        unique_together = [["restaurant", "table_number"]]
        indexes = [
            models.Index(fields=["qr_code_string"]),
        ]

    def __str__(self):
        return f"Table {self.table_number} @ {self.restaurant.name}"