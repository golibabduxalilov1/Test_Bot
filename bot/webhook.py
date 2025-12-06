import json
import logging
import asyncio
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

# Global variable to store the application instance
_application = None
_application_lock = asyncio.Lock()


async def get_application():
    global _application
    async with _application_lock:
        if _application is None:
            _application = (
                Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            )

            _application.add_handler(CommandHandler("start", BotHandlers.start_command))
            _application.add_handler(CommandHandler("help", BotHandlers.help_command))

            _application.add_handler(
                MessageHandler(filters.CONTACT, BotHandlers.contact_handler)
            )

            _application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^➕ Yangi test$"),
                    BotHandlers.create_test_start,
                )
            )
            _application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📝 Mening testlarim$"),
                    BotHandlers.my_tests_handler,
                )
            )

            _application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📝 Mavjud testlar$"),
                    BotHandlers.available_tests_handler,
                )
            )
            _application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^📊 Natijalarim$"),
                    BotHandlers.my_results_handler,
                )
            )

            _application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    BotHandlers.create_test_name_handler,
                )
            )
            _application.add_handler(
                MessageHandler(
                    filters.Document.ALL | filters.PHOTO,
                    BotHandlers.create_test_file_handler,
                )
            )

            _application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.Regex("^❌ Bekor qilish$"),
                    BotHandlers.cancel_handler,
                )
            )

            _application.add_handler(CallbackQueryHandler(BotHandlers.callback_handler))

            _application.add_handler(
                MessageHandler(filters.ALL, BotHandlers.unknown_message_handler)
            )

            await _application.initialize()

    return _application


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebhookView(View):

    async def post(self, request):
        try:
            application = await get_application()

            update_data = json.loads(request.body)
            update = Update.de_json(update_data, application.bot)

            await application.process_update(update)

            return JsonResponse({"ok": True})

        except Exception as e:
            logger.error(f"Webhook xatolik: {str(e)}")
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    async def get(self, request):
        return HttpResponse("Telegram Bot Webhook")
