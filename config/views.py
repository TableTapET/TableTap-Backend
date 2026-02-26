from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class NotImplementedView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"detail": "This endpoint is not implemented yet."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )