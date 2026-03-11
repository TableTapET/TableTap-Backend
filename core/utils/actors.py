"""
Unified actor resolution for TableTap requests.

Usage::

    from core.utils.actors import get_current_actor

    actor = get_current_actor(request)
    if actor is None:
        # completely anonymous — no session guest either
        ...
    elif isinstance(actor, User):
        # authenticated staff / manager / owner / customer
        ...
    elif isinstance(actor, GuestUser):
        # anonymous guest with a session
        ...
"""

from typing import Union

from apps.accounts.models import GuestUser, User


def get_current_actor(request) -> Union[User, GuestUser, None]:
    """
    Return the current actor for a request.

    Resolution order:
    1. If the request has an authenticated ``User``, return it.
    2. If the ``GuestUserMiddleware`` attached a ``GuestUser``, return it.
    3. Otherwise return ``None``.
    """
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return user

    guest = getattr(request, "guest_user", None)
    if guest is not None:
        return guest

    return None
