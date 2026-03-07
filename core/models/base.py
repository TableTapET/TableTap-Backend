import uuid

from django.db import models


class UUIDModel(models.Model):
    """
    UUID model class can be used in other models to avoid duplicate values.
    The class provides a UUID primary key with automatic generation and immutability.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    """
    Timestamp model class can be used in other models to avoid duplicate values.
    The class provides the 'created_at' and 'updated_at' values inside it with
    default settings.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Avoid creating migration
        abstract = True
