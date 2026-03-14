from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import GuestUser
from apps.accounts.serializers import (
    GuestUserSerializer,
    LoginSerializer,
    SignupSerializer,
    UserSerializer,
)

# ---------------------------------------------------------------------------
# Helper – set JWT cookies on a response
# ---------------------------------------------------------------------------


def _set_jwt_cookies(response, access_token, refresh_token):
    """Attach access & refresh tokens as HttpOnly cookies."""
    jwt_cfg = settings.SIMPLE_JWT
    cookie_kwargs = {
        "httponly": jwt_cfg.get("AUTH_COOKIE_HTTP_ONLY", True),
        "secure": jwt_cfg.get("AUTH_COOKIE_SECURE", False),
        "samesite": jwt_cfg.get("AUTH_COOKIE_SAMESITE", "Lax"),
        "path": jwt_cfg.get("AUTH_COOKIE_PATH", "/"),
    }
    response.set_cookie(
        jwt_cfg.get("AUTH_COOKIE", "access_token"),
        str(access_token),
        max_age=int(jwt_cfg["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **cookie_kwargs,
    )
    response.set_cookie(
        jwt_cfg.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        str(refresh_token),
        max_age=int(jwt_cfg["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        **cookie_kwargs,
    )
    return response


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------


class LoginView(APIView):
    """
    POST /api/user/login/
    Authenticate with username + password; tokens are set as HttpOnly cookies.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response = Response(
            {"detail": "Login successful."},
            status=status.HTTP_200_OK,
        )
        return _set_jwt_cookies(response, refresh.access_token, refresh)


class SignupView(APIView):
    """
    POST /api/user/signup/
    Create a new customer account.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Signup successful."},
            status=status.HTTP_201_CREATED,
        )


class RefreshView(APIView):
    """
    POST /api/user/refresh_token/
    Read the refresh cookie, rotate tokens, set new cookies.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        jwt_cfg = settings.SIMPLE_JWT
        raw_refresh = request.COOKIES.get(
            jwt_cfg.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )
        if raw_refresh is None:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            refresh = RefreshToken(raw_refresh)
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Blacklist the old refresh token if rotation is enabled
        if jwt_cfg.get("ROTATE_REFRESH_TOKENS"):
            try:
                refresh.blacklist()
            except AttributeError:
                pass

        # Re-fetch user for new token pair
        from apps.accounts.models import User

        user_id = refresh.payload.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        new_refresh = RefreshToken.for_user(user)

        response = Response(
            {"detail": "Token refreshed."},
            status=status.HTTP_200_OK,
        )
        return _set_jwt_cookies(response, new_refresh.access_token, new_refresh)


class LogoutView(APIView):
    """
    POST /api/user/logout/
    Blacklist the refresh token and delete both cookies.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        jwt_cfg = settings.SIMPLE_JWT
        raw_refresh = request.COOKIES.get(
            jwt_cfg.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )
        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except Exception:
                pass

        response = Response(
            {"detail": "Logged out."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie(
            jwt_cfg.get("AUTH_COOKIE", "access_token"),
            path=jwt_cfg.get("AUTH_COOKIE_PATH", "/"),
        )
        response.delete_cookie(
            jwt_cfg.get("AUTH_COOKIE_REFRESH", "refresh_token"),
            path=jwt_cfg.get("AUTH_COOKIE_PATH", "/"),
        )
        return response


class MeView(APIView):
    """
    GET /api/user/me/
    Return the profile of the currently authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GuestUserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing GuestUser sessions.

    - POST   /api/user/guests/       → create a guest tied to the current session
    - GET    /api/user/guests/{id}/   → retrieve a guest by PK
    """

    queryset = GuestUser.objects.select_related("restaurant")
    serializer_class = GuestUserSerializer
    # No authentication required – guests are anonymous by definition
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        """
        Create a GuestUser using the current Django session key.
        If the session already has a GuestUser, return the existing one.
        """
        # Ensure a session exists
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        # Return existing guest if one already exists for this session
        existing = GuestUser.objects.filter(session_key=session_key).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(session_key=session_key)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
