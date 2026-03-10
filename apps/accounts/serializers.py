from rest_framework import serializers

from apps.accounts.models import GuestUser


class GuestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestUser
        fields = ["id", "session_key", "restaurant", "created_at"]
        read_only_fields = ["id", "session_key", "created_at"]
