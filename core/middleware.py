from apps.accounts.models import GuestUser


class GuestUserMiddleware:
    """
    Middleware that automatically creates or retrieves a GuestUser
    for every anonymous (unauthenticated) request that carries a session.

    After processing, ``request.guest_user`` is set to the GuestUser
    instance when the visitor is anonymous, or ``None`` when the
    request belongs to an authenticated user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Default – no guest on the request
        request.guest_user = None

        if not getattr(request, "user", None) or not request.user.is_authenticated:
            # Ensure a session key exists
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            request.guest_user = GuestUser.objects.filter(
                session_key=session_key,
            ).first()

        response = self.get_response(request)
        return response
