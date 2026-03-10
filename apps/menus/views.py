from rest_framework import viewsets

from apps.menus.models import MenuCategory
from apps.menus.serializers import MenuCategorySerializer
from core.permissions import IsRestaurantStaff


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """CRUD for menu categories, scoped to the user's restaurant."""

    serializer_class = MenuCategorySerializer
    permission_classes = [IsRestaurantStaff]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return MenuCategory.objects.filter(
            menu__restaurant=self.request.user.restaurant
        )
