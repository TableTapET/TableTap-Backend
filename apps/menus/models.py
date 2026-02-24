from django.db import models


class Menu(models.Model):
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="menus",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    available_start_time = models.TimeField(blank=True, null=True)
    available_end_time = models.TimeField(blank=True, null=True)

    class Meta:
        db_table = "menus"
        indexes = [
            models.Index(fields=["restaurant", "is_available"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"


class MenuItem(models.Model):
    menu = models.ForeignKey(
        "menus.Menu",
        on_delete=models.CASCADE,
        related_name="items",
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    ingredients = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "menu_items"
        indexes = [
            models.Index(fields=["menu", "is_available"]),
            models.Index(fields=["restaurant"]),
        ]

    def __str__(self):
        return f"{self.name} - ${self.price}"