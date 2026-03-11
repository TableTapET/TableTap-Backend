"""
Cookie-based JWT authentication for DRF.

Reads the access token from an HttpOnly cookie instead of the
``Authorization`` header, enabling secure browser-based auth without
exposing tokens to JavaScript.
"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Extends ``JWTAuthentication`` to read the access token from
    the cookie named in ``settings.SIMPLE_JWT["AUTH_COOKIE"]``.

    Falls back to the standard ``Authorization`` header when
    no cookie is present, so API clients can still use headers.
    """

    def authenticate(self, request):
        cookie_name = settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token")
        raw_token = request.COOKIES.get(cookie_name)

        if raw_token is None:
            # Fall back to the header-based approach
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return user, validated_token
