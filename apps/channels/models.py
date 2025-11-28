from django.db import models


class GroupChannel(models.Model):
    CHANNEL_TYPE_CHOICES = [
        ("group", "Guruh"),
        ("channel", "Kanel"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nomi")
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Username"
    )
    invite_link = models.URLField(blank=True, null=True, verbose_name="Taklif linki")
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        default="channel",
        verbose_name="Turi",
    )
    is_mandatory = models.BooleanField(default=True, verbose_name="Majburiy a'zolik")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan")

    class Meta:
        db_table = "group_channels"
        verbose_name = "Guruh/Kanel"
        verbose_name_plural = "Guruh va Kanellar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"
