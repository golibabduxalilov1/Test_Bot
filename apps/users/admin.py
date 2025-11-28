from django.contrib import admin
from .models import User, BotState
from unfold.admin import ModelAdmin


@admin.register(User)
class UserAdmin(ModelAdmin):

    list_display = ("telegram_id", "phone_number")


@admin.register(BotState)
class BotStateAdmin(ModelAdmin):

    list_display = ("user", "state")
