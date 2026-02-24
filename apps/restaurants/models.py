from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "restaurants"

    def __str__(self):
        return self.name