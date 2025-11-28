from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import GroupChannel


@admin.register(GroupChannel)
class GroupChannelAdmin(ModelAdmin):

    list_display = ("username", "telegram_id")
