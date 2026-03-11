import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menus.models import Menu, MenuCategory, MenuItem
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
def menu_item(menu_a, category_a):
    return MenuItem.objects.create(
        menu=menu_a,
        category=category_a,
        name="Caesar Salad",
        description="Fresh romaine lettuce",
        price="9.99",
        is_available=True,
    )


@pytest.fixture
def menu_item_b(menu_b, category_b):
    return MenuItem.objects.create(
        menu=menu_b,
        category=category_b,
        name="Chocolate Cake",
        description="Rich chocolate layer cake",
        price="7.50",
        is_available=True,
    )


@pytest.fixture
def api_client():
    return APIClient()
