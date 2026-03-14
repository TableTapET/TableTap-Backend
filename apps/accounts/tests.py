import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.db import IntegrityError
from django.test import RequestFactory
from rest_framework.test import APIClient

from apps.accounts.models import GuestUser, User
from apps.restaurants.models import Restaurant
from core.middleware import GuestUserMiddleware
from core.utils.actors import get_current_actor

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def restaurant(db):
    return Restaurant.objects.create(name="Test Restaurant")


@pytest.fixture
def guest_user(db, restaurant):
    return GuestUser.objects.create(
        session_key="abc12345def67890", restaurant=restaurant
    )


@pytest.fixture
def api_client():
    return APIClient()


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuestUserModel:
    """Unit tests for the GuestUser model."""

    def test_create_guest_user(self, restaurant):
        guest = GuestUser.objects.create(
            session_key="sess_001",
            restaurant=restaurant,
        )
        assert guest.pk is not None
        assert guest.session_key == "sess_001"
        assert guest.restaurant == restaurant
        assert guest.created_at is not None
        assert guest.updated_at is not None

    def test_str_representation(self, guest_user):
        expected = (
            f"Guest({guest_user.session_key[:8]}...) @ {guest_user.restaurant.name}"
        )
        assert str(guest_user) == expected

    def test_session_key_unique(self, guest_user, restaurant):
        with pytest.raises(IntegrityError):
            GuestUser.objects.create(
                session_key=guest_user.session_key,
                restaurant=restaurant,
            )

    def test_cascade_delete_with_restaurant(self, guest_user):
        restaurant = guest_user.restaurant
        restaurant.delete()
        assert not GuestUser.objects.filter(pk=guest_user.pk).exists()

    def test_session_key_max_length(self, restaurant):
        long_key = "x" * 40
        guest = GuestUser.objects.create(session_key=long_key, restaurant=restaurant)
        assert guest.session_key == long_key


# ---------------------------------------------------------------------------
# Serializer Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuestUserSerializer:
    """Tests for the GuestUserSerializer."""

    def test_serializer_fields(self, guest_user):
        from apps.accounts.serializers import GuestUserSerializer

        serializer = GuestUserSerializer(instance=guest_user)
        data = serializer.data
        assert set(data.keys()) == {"id", "session_key", "restaurant", "created_at"}

    def test_serializer_read_only_fields(self):
        from apps.accounts.serializers import GuestUserSerializer

        serializer = GuestUserSerializer()
        read_only = {f.field_name for f in serializer.fields.values() if f.read_only}
        assert "id" in read_only
        assert "session_key" in read_only
        assert "created_at" in read_only


# ---------------------------------------------------------------------------
# API / Endpoint Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuestUserAPI:
    """Integration tests for the GuestUser endpoints."""

    GUESTS_URL = "/api/user/guests/"

    def test_create_guest_user(self, api_client, restaurant):
        response = api_client.post(
            self.GUESTS_URL,
            data={"restaurant": restaurant.pk},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["restaurant"] == restaurant.pk
        assert "session_key" in response.data
        assert "id" in response.data
        assert GuestUser.objects.count() == 1

    def test_create_guest_returns_existing_for_same_session(
        self, api_client, restaurant
    ):
        # First request – creates the guest
        resp1 = api_client.post(
            self.GUESTS_URL,
            data={"restaurant": restaurant.pk},
            format="json",
        )
        assert resp1.status_code == 201

        # Second request (same session) – returns existing
        resp2 = api_client.post(
            self.GUESTS_URL,
            data={"restaurant": restaurant.pk},
            format="json",
        )
        assert resp2.status_code == 200
        assert resp2.data["id"] == resp1.data["id"]
        assert GuestUser.objects.count() == 1

    def test_create_guest_requires_restaurant(self, api_client):
        response = api_client.post(self.GUESTS_URL, data={}, format="json")
        assert response.status_code == 400

    def test_retrieve_guest_user(self, api_client, guest_user):
        url = f"{self.GUESTS_URL}{guest_user.pk}/"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["session_key"] == guest_user.session_key

    def test_retrieve_nonexistent_guest(self, api_client):
        response = api_client.get(f"{self.GUESTS_URL}99999/")
        assert response.status_code == 404

    def test_guest_endpoint_allows_unauthenticated(self, api_client, restaurant):
        # No auth headers set — should still work
        response = api_client.post(
            self.GUESTS_URL,
            data={"restaurant": restaurant.pk},
            format="json",
        )
        assert response.status_code == 201


# ---------------------------------------------------------------------------
# Middleware Tests
# ---------------------------------------------------------------------------


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.mark.django_db
class TestGuestUserMiddleware:
    """Tests for the GuestUserMiddleware."""

    def _make_middleware(self, response_value=None):
        """Return a middleware instance with a dummy get_response."""
        return GuestUserMiddleware(lambda req: response_value)

    def test_anonymous_request_sets_guest_user_none_when_no_guest_exists(
        self, request_factory
    ):
        """Anonymous request with no matching GuestUser → request.guest_user is None."""
        middleware = self._make_middleware()
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.session.create()

        middleware(request)

        assert request.guest_user is None

    def test_anonymous_request_attaches_existing_guest(
        self, request_factory, restaurant
    ):
        """Anonymous request whose session already has a GuestUser → attached."""
        session = SessionStore()
        session.create()
        guest = GuestUser.objects.create(
            session_key=session.session_key, restaurant=restaurant
        )

        middleware = self._make_middleware()
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.session = session

        middleware(request)

        assert request.guest_user is not None
        assert request.guest_user.pk == guest.pk

    def test_authenticated_request_sets_guest_user_none(
        self, request_factory, restaurant
    ):
        """Authenticated users should never get a guest_user attached."""
        user = User.objects.create_user(
            username="staffuser", password="pass", role="staff"
        )
        middleware = self._make_middleware()
        request = request_factory.get("/")
        request.user = user
        request.session = SessionStore()

        middleware(request)

        assert request.guest_user is None

    def test_middleware_creates_session_key_if_missing(self, request_factory):
        """If the session has no key yet, the middleware should create one."""
        middleware = self._make_middleware()
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.session = SessionStore()
        assert request.session.session_key is None

        middleware(request)

        assert request.session.session_key is not None
        assert request.guest_user is None

    def test_middleware_does_not_overwrite_existing_session(
        self, request_factory, restaurant
    ):
        """Middleware should reuse the existing session key, not create a new one."""
        session = SessionStore()
        session.create()
        original_key = session.session_key

        guest = GuestUser.objects.create(
            session_key=original_key, restaurant=restaurant
        )

        middleware = self._make_middleware()
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.session = session

        middleware(request)

        assert request.session.session_key == original_key
        assert request.guest_user.pk == guest.pk


# ---------------------------------------------------------------------------
# Actor Resolver Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGetCurrentActor:
    """Tests for the get_current_actor utility."""

    def test_returns_authenticated_user(self, request_factory):
        """When request.user is authenticated, return the User."""
        user = User.objects.create_user(
            username="actor_user", password="pass", role="manager"
        )
        request = request_factory.get("/")
        request.user = user
        request.guest_user = None

        actor = get_current_actor(request)

        assert actor == user
        assert isinstance(actor, User)

    def test_returns_guest_user_when_anonymous(self, request_factory, guest_user):
        """When request.user is anonymous but guest_user exists, return GuestUser."""
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.guest_user = guest_user

        actor = get_current_actor(request)

        assert actor == guest_user
        assert isinstance(actor, GuestUser)

    def test_returns_none_when_fully_anonymous(self, request_factory):
        """When no user and no guest_user, return None."""
        request = request_factory.get("/")
        request.user = AnonymousUser()
        request.guest_user = None

        actor = get_current_actor(request)

        assert actor is None

    def test_prefers_authenticated_user_over_guest(self, request_factory, guest_user):
        """Even if guest_user is set, an authenticated user takes priority."""
        user = User.objects.create_user(
            username="priority_user", password="pass", role="staff"
        )
        request = request_factory.get("/")
        request.user = user
        request.guest_user = guest_user

        actor = get_current_actor(request)

        assert actor == user
        assert isinstance(actor, User)

    def test_handles_missing_user_attribute(self, request_factory):
        """If request has no user attribute at all, fall back gracefully."""
        request = request_factory.get("/")
        # Remove user attribute entirely
        if hasattr(request, "user"):
            del request.user
        request.guest_user = None

        actor = get_current_actor(request)

        assert actor is None


# ---------------------------------------------------------------------------
# JWT Authentication Tests
# ---------------------------------------------------------------------------

LOGIN_URL = "/api/user/login/"
LOGOUT_URL = "/api/user/logout/"
REFRESH_URL = "/api/user/refresh_token/"
ME_URL = "/api/user/me/"
SIGNUP_URL = "/api/user/signup/"


@pytest.fixture
def auth_user(db):
    return User.objects.create_user(
        username="jwtuser",
        password="testpass123",
        email="jwt@example.com",
        role="manager",
        name="JWT User",
    )


@pytest.mark.django_db
class TestLoginView:
    """Tests for POST /api/user/login/."""

    def test_login_success(self, api_client, auth_user):
        response = api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["detail"] == "Login successful."
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"]["httponly"]
        assert response.cookies["refresh_token"]["httponly"]

    def test_login_invalid_credentials(self, api_client, auth_user):
        response = api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == 400

    def test_login_missing_fields(self, api_client):
        response = api_client.post(LOGIN_URL, data={}, format="json")
        assert response.status_code == 400

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post(
            LOGIN_URL,
            data={"username": "noone", "password": "whatever"},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSignupView:
    """Tests for POST /api/user/signup/."""

    def test_signup_success(self, api_client):
        payload = {
            "username": "newcustomer",
            "email": "newcustomer@example.com",
            "password": "testpass123",
            "name": "New Customer",
            "phone_number": "+251900000000",
        }

        response = api_client.post(SIGNUP_URL, data=payload, format="json")

        assert response.status_code == 201
        assert response.data["detail"] == "Signup successful."
        user = User.objects.get(username="newcustomer")
        assert user.role == "customer"
        assert user.email == "newcustomer@example.com"
        assert user.check_password("testpass123")

    def test_signup_rejects_duplicate_username(self, api_client, auth_user):
        payload = {
            "username": auth_user.username,
            "email": "another@example.com",
            "password": "testpass123",
        }

        response = api_client.post(SIGNUP_URL, data=payload, format="json")

        assert response.status_code == 400
        assert "username" in response.data

    def test_signup_requires_minimum_password_length(self, api_client):
        payload = {
            "username": "shortpass",
            "email": "shortpass@example.com",
            "password": "short",
        }

        response = api_client.post(SIGNUP_URL, data=payload, format="json")

        assert response.status_code == 400
        assert "password" in response.data


@pytest.mark.django_db
class TestRefreshView:
    """Tests for POST /api/user/refresh_token/."""

    def test_refresh_success(self, api_client, auth_user):
        # First login to get cookies
        api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "testpass123"},
            format="json",
        )
        response = api_client.post(REFRESH_URL)
        assert response.status_code == 200
        assert response.data["detail"] == "Token refreshed."
        assert "access_token" in response.cookies

    def test_refresh_without_cookie(self, api_client):
        response = api_client.post(REFRESH_URL)
        assert response.status_code == 401
        assert response.data["detail"] == "Refresh token not found."

    def test_refresh_invalid_token(self, api_client):
        api_client.cookies.load({"refresh_token": "invalid.token.here"})
        response = api_client.post(REFRESH_URL)
        assert response.status_code == 401
        assert response.data["detail"] == "Invalid or expired refresh token."


@pytest.mark.django_db
class TestLogoutView:
    """Tests for POST /api/user/logout/."""

    def test_logout_clears_cookies(self, api_client, auth_user):
        # Login first
        api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "testpass123"},
            format="json",
        )
        response = api_client.post(LOGOUT_URL)
        assert response.status_code == 200
        assert response.data["detail"] == "Logged out."
        # Cookies are deleted (max-age=0)
        assert response.cookies["access_token"]["max-age"] == 0
        assert response.cookies["refresh_token"]["max-age"] == 0

    def test_logout_without_cookies(self, api_client):
        # Should still succeed gracefully
        response = api_client.post(LOGOUT_URL)
        assert response.status_code == 200


@pytest.mark.django_db
class TestMeView:
    """Tests for GET /api/user/me/."""

    def test_me_authenticated(self, api_client, auth_user):
        # Login to get cookies
        api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "testpass123"},
            format="json",
        )
        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["username"] == "jwtuser"
        assert response.data["email"] == "jwt@example.com"
        assert response.data["role"] == "manager"

    def test_me_unauthenticated(self, api_client):
        response = api_client.get(ME_URL)
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# CookieJWTAuthentication Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCookieJWTAuthentication:
    """Tests for the CookieJWTAuthentication backend."""

    def test_auth_via_cookie(self, api_client, auth_user):
        """Access token in cookie should authenticate the user."""
        api_client.post(
            LOGIN_URL,
            data={"username": "jwtuser", "password": "testpass123"},
            format="json",
        )
        # Cookie is automatically sent by the test client
        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["username"] == "jwtuser"

    def test_auth_via_header(self, api_client, auth_user):
        """Bearer token in Authorization header should also work."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(auth_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["username"] == "jwtuser"
