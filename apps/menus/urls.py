from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.menus.views import MenuCategoryViewSet

router = DefaultRouter()
router.register(r"categories", MenuCategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
