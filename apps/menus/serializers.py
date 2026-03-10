from rest_framework import serializers

from apps.menus.models import MenuCategory, MenuItem


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "menu",
            "name",
            "description",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_menu(self, value):
        """Ensure the menu belongs to the requesting user's restaurant."""
        request = self.context.get("request")
        if request and value.restaurant != request.user.restaurant:
            raise serializers.ValidationError(
                "Menu does not belong to your restaurant."
            )
        return value


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "menu",
            "category",
            "name",
            "description",
            "price",
            "is_available",
            "image_url",
            "ingredients",
        ]
        read_only_fields = ["id"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must not be negative.")
        return value

    def validate_menu(self, value):
        """Ensure the menu belongs to the requesting user's restaurant."""
        request = self.context.get("request")
        if request and value.restaurant != request.user.restaurant:
            raise serializers.ValidationError(
                "Menu does not belong to your restaurant."
            )
        return value

    def validate(self, attrs):
        """Ensure category belongs to the same menu."""
        menu = attrs.get("menu", getattr(self.instance, "menu", None))
        category = attrs.get("category", getattr(self.instance, "category", None))
        if menu and category and category.menu != menu:
            raise serializers.ValidationError(
                {"category": "Category does not belong to the selected menu."}
            )
        return attrs
