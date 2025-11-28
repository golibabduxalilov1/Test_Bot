from django.db import models
from django.core.validators import FileExtensionValidator


class Advertisement(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    text = models.TextField(verbose_name="Matn")
    image = models.ImageField(
        upload_to="ads/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        verbose_name="Rasm",
    )
    button_text = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Tugma matni"
    )
    button_url = models.URLField(blank=True, null=True, verbose_name="Tugma havolasi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    show_to_students = models.BooleanField(
        default=True, verbose_name="O'quvchilarga ko'rsatish"
    )
    show_to_teachers = models.BooleanField(
        default=False, verbose_name="O'qituvchilarga ko'rsatish"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        db_table = "advertisements"
        verbose_name = "Reklama"
        verbose_name_plural = "Reklamalar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
