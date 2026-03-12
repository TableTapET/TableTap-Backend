from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Checks if the role of an authenticated user matches the "owner" role.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role == "owner"


class IsManager(BasePermission):
    """
    Checks if the role of an authenticated user matches the "manager" role.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role == "manager"


class IsStaff(BasePermission):
    """
    Checks if the role of an authenticated user matches the "staff" role.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role == "staff"


class IsCustomer(BasePermission):
    """
    Checks if the role of an authenticated user matches the "customer" role.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role == "customer"


class IsOwnerOrManager(BasePermission):
    """
    Combined permission for admin-level actions.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role in (
            "owner",
            "manager",
        )


class IsRestaurantStaff(BasePermission):
    """
    Allow access to authenticated users with owner, manager, or staff roles.
    """

    def has_permission(self, request, __view__):
        return request.user.is_authenticated and request.user.role in (
            "owner",
            "manager",
            "staff",
        )
