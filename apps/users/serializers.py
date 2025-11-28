from rest_framework import serializers
from .models import User, BotState


class UserSerializer(serializers.ModelSerializer):

    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "telegram_id",
            "username",
            "full_name",
            "phone_number",
            "role",
            "role_display",
            "is_phone_verified",
            "is_channel_member",
            "joined_at",
            "last_activity",
            "is_blocked",
        ]
        read_only_fields = ["id", "joined_at", "last_activity"]


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["telegram_id", "full_name", "phone_number", "role"]

    def create(self, validated_data):
        validated_data["username"] = f"user_{validated_data['telegram_id']}"
        return super().create(validated_data)


class BotStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotState
        fields = ["user", "state", "data", "updated_at"]
