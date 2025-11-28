from rest_framework import serializers
from .models import GroupChannel


class GroupChannelSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_channel_type_display", read_only=True
    )

    class Meta:
        model = GroupChannel
        fields = [
            "id",
            "name",
            "telegram_id",
            "username",
            "invite_link",
            "channel_type",
            "type_display",
            "is_mandatory",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
