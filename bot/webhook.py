"""Webhook view"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from django.conf import settings

from .handlers import BotHandlers
from .states import BotStates

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application = None

    async def setup_application(self):
        """Application ni sozlash"""
        if self.application is None:
            self.application = (
                Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            )

            self.application.add_handler(
                CommandHandler("start", BotHandlers.start_command)
            )
            self.application.add_handler(
                CommandHandler("help", BotHandlers.help_command)
            )

            self.application.add_handler(
                MessageHandler(filters.CONTACT, BotHandlers.contact_handler)
            )

            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^➕ Yangi test$"),
                    BotHandlers.create_test_start,
                )
            )
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📝 Mening testlarim$"),
                    BotHandlers.my_tests_handler,
                )
            )

            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📝 Mavjud testlar$"),
                    BotHandlers.available_tests_handler,
                )
            )
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📊 Natijalarim$"),
                    BotHandlers.my_results_handler,
                )
            )

            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    BotHandlers.create_test_name_handler,
                )
            )
            self.application.add_handler(
                MessageHandler(
                    filters.Document.ALL | filters.PHOTO,
                    BotHandlers.create_test_file_handler,
                )
            )

            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^❌ Bekor qilish$"),
                    BotHandlers.cancel_handler,
                )
            )

            self.application.add_handler(
                CallbackQueryHandler(BotHandlers.callback_handler)
            )

            self.application.add_handler(
                MessageHandler(filters.ALL, BotHandlers.unknown_message_handler)
            )

            await self.application.initialize()

    async def post(self, request):
        try:
            await self.setup_application()

            update_data = json.loads(request.body)
            update = Update.de_json(update_data, self.application.bot)

            await self.application.process_update(update)

            return JsonResponse({"ok": True})

        except Exception as e:
            logger.error(f"Webhook xatolik: {str(e)}")
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    async def get(self, request):
        return HttpResponse("Telegram Bot Webhook")
