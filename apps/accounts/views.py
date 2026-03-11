from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.accounts.models import GuestUser
from apps.accounts.serializers import GuestUserSerializer


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
