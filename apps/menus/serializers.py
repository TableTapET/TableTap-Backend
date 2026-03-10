from rest_framework import serializers

from apps.menus.models import MenuCategory


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
