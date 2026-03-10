from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.menus.views import MenuCategoryViewSet, MenuItemViewSet

router = DefaultRouter()
router.register(r"categories", MenuCategoryViewSet, basename="category")
router.register(r"items", MenuItemViewSet, basename="menuitem")

urlpatterns = [
    path("", include(router.urls)),
]
