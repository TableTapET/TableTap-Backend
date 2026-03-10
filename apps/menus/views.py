from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.menus.models import MenuCategory, MenuItem
from apps.menus.serializers import MenuCategorySerializer, MenuItemSerializer
from core.permissions import IsRestaurantStaff


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """CRUD for menu categories, scoped to the user's restaurant."""

    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return MenuCategory.objects.filter(
            menu__restaurant=self.request.user.restaurant
        )


class MenuItemViewSet(viewsets.ModelViewSet):
    """CRUD for menu items, scoped to the user's restaurant."""

    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsRestaurantStaff]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return MenuItem.objects.filter(menu__restaurant=self.request.user.restaurant)
