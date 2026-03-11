from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    GuestUserViewSet,
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
)

router = DefaultRouter()
router.register(r"guests", GuestUserViewSet, basename="guest-user")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh_token/", RefreshView.as_view(), name="refresh_token"),
    path("me/", MeView.as_view(), name="me"),
]
