import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menus.models import Menu, MenuCategory
from apps.restaurants.models import Restaurant


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def restaurant_a():
    return Restaurant.objects.create(name="Restaurant A")


@pytest.fixture
def restaurant_b():
    return Restaurant.objects.create(name="Restaurant B")


@pytest.fixture
def owner(restaurant_a):
    return User.objects.create_user(
        username="owner",
        password="testpass123",
        role="owner",
        restaurant=restaurant_a,
    )


@pytest.fixture
def manager(restaurant_a):
    return User.objects.create_user(
        username="manager",
        password="testpass123",
        role="manager",
        restaurant=restaurant_a,
    )


@pytest.fixture
def staff_user(restaurant_a):
    return User.objects.create_user(
        username="staffuser",
        password="testpass123",
        role="staff",
        restaurant=restaurant_a,
    )


@pytest.fixture
def customer(restaurant_a):
    return User.objects.create_user(
        username="customer",
        password="testpass123",
        role="customer",
        restaurant=restaurant_a,
    )


@pytest.fixture
def other_owner(restaurant_b):
    return User.objects.create_user(
        username="other_owner",
        password="testpass123",
        role="owner",
        restaurant=restaurant_b,
    )


@pytest.fixture
def menu_a(restaurant_a):
    return Menu.objects.create(
        restaurant=restaurant_a,
        name="Lunch Menu",
        description="Served 11am-3pm",
        is_available=True,
    )


@pytest.fixture
def menu_b(restaurant_b):
    return Menu.objects.create(
        restaurant=restaurant_b,
        name="Dinner Menu",
        description="Served 5pm-10pm",
        is_available=True,
    )


@pytest.fixture
def category_a(menu_a):
    return MenuCategory.objects.create(
        menu=menu_a,
        name="Appetizers",
        description="Starters and small plates",
        is_available=True,
    )


@pytest.fixture
def category_b(menu_b):
    return MenuCategory.objects.create(
        menu=menu_b,
        name="Desserts",
        description="Sweet treats",
        is_available=True,
    )


@pytest.fixture
def api_client():
    return APIClient()


# ---------------------------------------------------------------------------
# TAB-42: Menu Category CRUD Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoryList:
    """GET /api/menu/categories/"""

    def test_owner_can_list_categories(self, api_client, owner, category_a):
        api_client.force_authenticate(user=owner)
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Appetizers"

    def test_staff_can_list_categories(self, api_client, staff_user, category_a):
        api_client.force_authenticate(user=staff_user)
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_customer_cannot_list_categories(self, api_client, customer, category_a):
        api_client.force_authenticate(user=customer)
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_list_categories(self, api_client, category_a):
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_isolation(
        self, api_client, owner, category_a, category_b
    ):
        """Owner of restaurant A should not see restaurant B's categories."""
        api_client.force_authenticate(user=owner)
        url = reverse("category-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Appetizers"


@pytest.mark.django_db
class TestCategoryCreate:
    """POST /api/menu/categories/"""

    def test_owner_can_create_category(self, api_client, owner, menu_a):
        api_client.force_authenticate(user=owner)
        url = reverse("category-list")
        data = {
            "menu": menu_a.pk,
            "name": "Main Course",
            "description": "Entrees",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Main Course"
        assert MenuCategory.objects.filter(name="Main Course", menu=menu_a).exists()

    def test_manager_can_create_category(self, api_client, manager, menu_a):
        api_client.force_authenticate(user=manager)
        url = reverse("category-list")
        data = {
            "menu": menu_a.pk,
            "name": "Beverages",
            "description": "Drinks",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_customer_cannot_create_category(self, api_client, customer, menu_a):
        api_client.force_authenticate(user=customer)
        url = reverse("category-list")
        data = {
            "menu": menu_a.pk,
            "name": "Secret Menu",
            "description": "Hidden",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_category_missing_name(self, api_client, owner, menu_a):
        api_client.force_authenticate(user=owner)
        url = reverse("category-list")
        data = {"menu": menu_a.pk, "description": "No name provided"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_cross_restaurant_menu_rejected(
        self, api_client, owner, menu_b
    ):
        """Cannot create a category under a menu from another restaurant."""
        api_client.force_authenticate(user=owner)
        url = reverse("category-list")
        data = {
            "menu": menu_b.pk,
            "name": "Sneaky Category",
            "description": "Should fail",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "menu" in response.data


@pytest.mark.django_db
class TestCategoryUpdate:
    """PATCH /api/menu/categories/{id}/"""

    def test_owner_can_update_category(self, api_client, owner, category_a):
        api_client.force_authenticate(user=owner)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.patch(url, {"name": "Updated Appetizers"})

        assert response.status_code == status.HTTP_200_OK
        category_a.refresh_from_db()
        assert category_a.name == "Updated Appetizers"

    def test_customer_cannot_update_category(self, api_client, customer, category_a):
        api_client.force_authenticate(user=customer)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.patch(url, {"name": "Hacked"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_update_returns_404(
        self, api_client, other_owner, category_a
    ):
        """Owner of restaurant B cannot update restaurant A's category."""
        api_client.force_authenticate(user=other_owner)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.patch(url, {"name": "Hijacked"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryDelete:
    """DELETE /api/menu/categories/{id}/"""

    def test_owner_can_delete_category(self, api_client, owner, category_a):
        api_client.force_authenticate(user=owner)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MenuCategory.objects.filter(pk=category_a.pk).exists()

    def test_customer_cannot_delete_category(self, api_client, customer, category_a):
        api_client.force_authenticate(user=customer)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_delete_returns_404(
        self, api_client, other_owner, category_a
    ):
        api_client.force_authenticate(user=other_owner)
        url = reverse("category-detail", kwargs={"pk": category_a.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

