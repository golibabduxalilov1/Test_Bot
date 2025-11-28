from django.urls import path
from .webhook import TelegramWebhookView

app_name = "bot"

urlpatterns = [
    path("telegram/", TelegramWebhookView.as_view(), name="telegram-webhook"),
]
