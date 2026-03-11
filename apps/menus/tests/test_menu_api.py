import pytest
from django.urls import reverse
from rest_framework import status

from apps.menus.models import MenuCategory, MenuItem

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


# ---------------------------------------------------------------------------
# TAB-43: Menu Item CRUD Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMenuItemList:
    """GET /api/menu/items/"""

    def test_owner_can_list_items(self, api_client, owner, menu_item):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Caesar Salad"

    def test_staff_can_list_items(self, api_client, staff_user, menu_item):
        api_client.force_authenticate(user=staff_user)
        url = reverse("menuitem-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_customer_cannot_list_items(self, api_client, customer, menu_item):
        api_client.force_authenticate(user=customer)
        url = reverse("menuitem-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_list_items(self, api_client, menu_item):
        url = reverse("menuitem-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_isolation(
        self, api_client, owner, menu_item, menu_item_b
    ):
        """Owner of restaurant A should not see restaurant B's items."""
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Caesar Salad"


@pytest.mark.django_db
class TestMenuItemCreate:
    """POST /api/menu/items/"""

    def test_owner_can_create_item(self, api_client, owner, menu_a, category_a):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_a.pk,
            "category": category_a.pk,
            "name": "Garlic Bread",
            "description": "Toasted with butter",
            "price": "4.50",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Garlic Bread"
        assert MenuItem.objects.filter(name="Garlic Bread", menu=menu_a).exists()

    def test_manager_can_create_item(self, api_client, manager, menu_a, category_a):
        api_client.force_authenticate(user=manager)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_a.pk,
            "category": category_a.pk,
            "name": "Soup of the Day",
            "description": "Ask your server",
            "price": "5.00",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_customer_cannot_create_item(
        self, api_client, customer, menu_a, category_a
    ):
        api_client.force_authenticate(user=customer)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_a.pk,
            "category": category_a.pk,
            "name": "Secret Item",
            "price": "99.99",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_item_negative_price_rejected(
        self, api_client, owner, menu_a, category_a
    ):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_a.pk,
            "category": category_a.pk,
            "name": "Bad Item",
            "price": "-1.00",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data

    def test_create_item_cross_restaurant_menu_rejected(
        self, api_client, owner, menu_b, category_b
    ):
        """Cannot create an item under a menu from another restaurant."""
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_b.pk,
            "category": category_b.pk,
            "name": "Sneaky Item",
            "price": "10.00",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "menu" in response.data

    def test_create_item_mismatched_category_rejected(
        self, api_client, owner, menu_a, category_b
    ):
        """Cannot assign a category from a different menu."""
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-list")
        data = {
            "menu": menu_a.pk,
            "category": category_b.pk,
            "name": "Mismatched Item",
            "price": "8.00",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "category" in response.data


@pytest.mark.django_db
class TestMenuItemUpdate:
    """PATCH /api/menu/items/{id}/"""

    def test_owner_can_update_item(self, api_client, owner, menu_item):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.patch(url, {"name": "Updated Salad"})

        assert response.status_code == status.HTTP_200_OK
        menu_item.refresh_from_db()
        assert menu_item.name == "Updated Salad"

    def test_owner_can_update_price(self, api_client, owner, menu_item):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.patch(url, {"price": "12.99"})

        assert response.status_code == status.HTTP_200_OK
        menu_item.refresh_from_db()
        assert str(menu_item.price) == "12.99"

    def test_customer_cannot_update_item(self, api_client, customer, menu_item):
        api_client.force_authenticate(user=customer)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.patch(url, {"name": "Hacked"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_update_returns_404(
        self, api_client, other_owner, menu_item
    ):
        """Owner of restaurant B cannot update restaurant A's item."""
        api_client.force_authenticate(user=other_owner)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.patch(url, {"name": "Hijacked"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestMenuItemDelete:
    """DELETE /api/menu/items/{id}/"""

    def test_owner_can_delete_item(self, api_client, owner, menu_item):
        api_client.force_authenticate(user=owner)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MenuItem.objects.filter(pk=menu_item.pk).exists()

    def test_customer_cannot_delete_item(self, api_client, customer, menu_item):
        api_client.force_authenticate(user=customer)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cross_restaurant_delete_returns_404(
        self, api_client, other_owner, menu_item
    ):
        api_client.force_authenticate(user=other_owner)
        url = reverse("menuitem-detail", kwargs={"pk": menu_item.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
