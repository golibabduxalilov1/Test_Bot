from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
import asyncio


class Command(BaseCommand):
    help = "Sets the Telegram bot webhook URL"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR("TELEGRAM_BOT_TOKEN is not set in settings.")
            )
            return

        if not settings.WEBHOOK_URL:
            self.stdout.write(self.style.ERROR("WEBHOOK_URL is not set in settings."))
            return

        webhook_url = f"{settings.WEBHOOK_URL}/api/webhook/telegram/"

        # Asyncio run setup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            webhook_info = loop.run_until_complete(bot.get_webhook_info())

            self.stdout.write(f"Current webhook URL: {webhook_info.url}")

            if webhook_info.url != webhook_url:
                self.stdout.write(f"Setting webhook URL to: {webhook_url}")
                loop.run_until_complete(bot.set_webhook(url=webhook_url))
                self.stdout.write(self.style.SUCCESS("Webhook set successfully!"))
            else:
                self.stdout.write(
                    self.style.SUCCESS("Webhook is already set correctly.")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting webhook: {e}"))
        finally:
            loop.close()
