from django.db import models


class Customer(models.Model):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "customers"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        return self.name