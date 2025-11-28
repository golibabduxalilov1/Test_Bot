from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class UserRole(models.TextChoices):
    """Foydalanuvchi rollari"""

    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "O'qituvchi"
    STUDENT = "student", "O'quvchi"


class User(AbstractUser):

    telegram_id = models.BigIntegerField(
        unique=True, db_index=True, verbose_name="Telegram ID", null=True, blank=True
    )
    phone_regex = RegexValidator(
        regex=r"^\+?998\d{9}$",
        message="Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak",
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        blank=True,
        null=True,
        verbose_name="Telefon raqami",
    )
    full_name = models.CharField(max_length=255, verbose_name="To'liq ismi")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        verbose_name="Rol",
    )
    is_phone_verified = models.BooleanField(
        default=False, verbose_name="Telefon tasdiqlangan"
    )
    is_channel_member = models.BooleanField(default=False, verbose_name="Kanalga a'zo")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan sana")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Oxirgi faollik")
    is_blocked = models.BooleanField(default=False, verbose_name="Bloklangan")

    class Meta:
        db_table = "users"
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT


class BotState(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="bot_state",
        verbose_name="Foydalanuvchi",
    )
    state = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Holat"
    )
    data = models.JSONField(default=dict, blank=True, verbose_name="Ma'lumotlar")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        db_table = "bot_states"
        verbose_name = "Bot holati"
        verbose_name_plural = "Bot holatlari"

    def __str__(self):
        return f"{self.user.full_name} - {self.state}"
