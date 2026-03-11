from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import GuestUserViewSet
from config.views import NotImplementedView

router = DefaultRouter()
router.register(r"guests", GuestUserViewSet, basename="guest-user")

urlpatterns = [
    path("", include(router.urls)),
    # These are template API, replace when actual functions are built out
    path("login/", NotImplementedView.as_view(), name="login"),
    path("logout/", NotImplementedView.as_view(), name="logout"),
    path("edit_user/", NotImplementedView.as_view(), name="edit_user"),
    path("refresh_token/", NotImplementedView.as_view(), name="refresh_token"),
    path("validate_token/", NotImplementedView.as_view(), name="validate_token"),
]
