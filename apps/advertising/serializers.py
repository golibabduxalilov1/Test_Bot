from rest_framework import serializers
from .models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "text",
            "image",
            "button_text",
            "button_url",
            "is_active",
            "show_to_students",
            "show_to_teachers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
