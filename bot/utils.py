import requests
from django.conf import settings
from telegram import Bot
from apps.users.models import User, BotState
from apps.channels.models import GroupChannel


class BotUtils:

    @staticmethod
    def get_or_create_user(telegram_user):
        user, created = User.objects.get_or_create(
            telegram_id=telegram_user.id,
            defaults={
                "username": telegram_user.username or f"user_{telegram_user.id}",
                "full_name": telegram_user.full_name,
            },
        )

        if user.telegram_id in settings.ADMIN_TELEGRAM_IDS and user.role != "admin":
            user.role = "admin"
            user.save()

        return user, created

    @staticmethod
    def get_user_state(user):
        bot_state, _ = BotState.objects.get_or_create(user=user)
        return bot_state

    @staticmethod
    def set_user_state(user, state, data=None):
        bot_state, _ = BotState.objects.get_or_create(user=user)
        bot_state.state = state
        if data is not None:
            bot_state.data = data
        bot_state.save()
        return bot_state

    @staticmethod
    def clear_user_state(user):
        BotState.objects.filter(user=user).update(state="idle", data={})

    @staticmethod
    async def check_channel_membership(bot: Bot, user_telegram_id: int):
        mandatory_channels = GroupChannel.objects.filter(
            is_active=True, is_mandatory=True
        )

        if not mandatory_channels.exists():
            return True  # Majburiy kanal yo'q bo'lsa, true qaytarish

        for channel in mandatory_channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel.telegram_id, user_id=user_telegram_id
                )

                # A'zo bo'lmasa
                if member.status in ["left", "kicked"]:
                    return False
            except Exception as e:
                print(f"Kanalga a'zolikni tekshirishda xatolik: {e}")
                return False

        return True

    @staticmethod
    def format_test_result(student_answer):
        """Test natijasini formatlash"""
        result_text = f"""
📊 <b>Test natijalari</b>

📝 Test: {student_answer.test.title}
👤 O'quvchi: {student_answer.student.full_name}

✅ To'g'ri javoblar: {student_answer.correct_count}
❌ Noto'g'ri javoblar: {student_answer.incorrect_count}
📈 Foiz: {student_answer.score_percentage:.2f}%

"""

        if student_answer.wrong_questions:
            result_text += "<b>Xato savollar:</b>\n"
            for wrong in student_answer.wrong_questions:
                result_text += f"• Savol {wrong['question']}: Sizning javobingiz {wrong['student_answer']}, to'g'ri javob {wrong['correct_answer']}\n"

        return result_text

    @staticmethod
    def weekday_to_english(uzbek_day):
        days_map = {
            "Dushanba": "monday",
            "Seshanba": "tuesday",
            "Chorshanba": "wednesday",
            "Payshanba": "thursday",
            "Juma": "friday",
            "Shanba": "saturday",
            "Yakshanba": "sunday",
        }
        return days_map.get(uzbek_day, "monday")

    @staticmethod
    def format_time(time_str):
        from datetime import datetime

        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            return time_obj
        except:
            return None

    @staticmethod
    def delete_message_safe(update, context):
        try:
            update.message.delete()
        except Exception as e:
            print(f"Xabarni o'chirishda xatolik: {e}")
