from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
import asyncio

class Command(BaseCommand):
    help = "Deletes the Telegram bot webhook"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set in settings."))
            return

        # Asyncio run setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

            self.stdout.write("Deleting webhook...")
            loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
            self.stdout.write(self.style.SUCCESS("Webhook deleted successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error deleting webhook: {e}"))
        finally:
            loop.close()
