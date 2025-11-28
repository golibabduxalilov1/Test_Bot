"""Telegram bot handlarlari"""

import os
import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from django.conf import settings

from .keyboards import BotKeyboards
from .states import BotStates
from .utils import BotUtils
from .filters import admin_filter, teacher_filter, student_filter

from apps.users.models import User
from apps.tests.models import Test, AnswerKey, StudentAnswer
from apps.channels.models import GroupChannel
from apps.advertising.models import Advertisement


class BotHandlers:

    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        user, created = BotUtils.get_or_create_user(telegram_user)

        if created or not user.is_phone_verified:
            # Telefon raqamini so'rash
            await update.message.reply_text(
                "👋 Assalomu alaykum!\n\n"
                "Botdan foydalanish uchun telefon raqamingizni ulashing.",
                reply_markup=BotKeyboards.phone_request(),
            )
            BotUtils.set_user_state(user, BotStates.WAITING_PHONE)
            return

        # Kanalga a'zolikni tekshirish
        is_member = await BotUtils.check_channel_membership(
            context.bot, telegram_user.id
        )

        if not is_member:
            mandatory_channel = GroupChannel.objects.filter(
                is_active=True, is_mandatory=True
            ).first()

            if mandatory_channel:
                await update.message.reply_text(
                    "❗️ Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:",
                    reply_markup=BotKeyboards.channel_check(
                        mandatory_channel.invite_link
                        or f"https://t.me/{mandatory_channel.username}"
                    ),
                )
                return

        # Rolga mos menyu ko'rsatish
        if user.is_admin:
            keyboard = BotKeyboards.main_menu_admin()
            welcome_text = "🔐 Admin paneliga xush kelibsiz!"
        elif user.is_teacher:
            keyboard = BotKeyboards.main_menu_teacher()
            welcome_text = "👨‍🏫 O'qituvchi paneliga xush kelibsiz!"
        else:
            keyboard = BotKeyboards.main_menu_student()
            welcome_text = "📚 Test botiga xush kelibsiz!"

        await update.message.reply_text(welcome_text, reply_markup=keyboard)
        BotUtils.clear_user_state(user)

    @staticmethod
    async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        contact = update.message.contact

        if not contact:
            return

        try:
            user = User.objects.get(telegram_id=update.effective_user.id)
            user.phone_number = contact.phone_number
            user.is_phone_verified = True
            user.save()

            await update.message.reply_text(
                "✅ Telefon raqamingiz tasdiqlandi!\n\n"
                "Endi /start buyrug'ini bosing.",
                reply_markup=BotKeyboards.back(),
            )
            BotUtils.clear_user_state(user)

        except User.DoesNotExist:
            await update.message.reply_text(
                "❌ Xatolik yuz berdi. /start ni qayta bosing."
            )

    @staticmethod
    async def create_test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = User.objects.get(telegram_id=update.effective_user.id)

        if not user.is_teacher and not user.is_admin:
            await update.message.reply_text("❌ Sizda test yaratish huquqi yo'q.")
            return

        await update.message.reply_text(
            "📝 Yangi test yaratish\n\n" "1️⃣ Test nomini kiriting:",
            reply_markup=BotKeyboards.cancel(),
        )
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_NAME)

    @staticmethod
    async def create_test_name_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_NAME:
            return

        test_name = update.message.text.strip()

        if len(test_name) < 3:
            await update.message.reply_text(
                "❌ Test nomi kamida 3 ta belgidan iborat bo'lishi kerak."
            )
            return

        # State data ga saqlash
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_FILE, {"title": test_name})

        await update.message.reply_text(
            "2️⃣ Test faylini yuboring (PDF, DOCX yoki rasm):",
            reply_markup=BotKeyboards.cancel(),
        )

    @staticmethod
    async def create_test_file_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_FILE:
            return

        file = None
        file_extension = None

        if update.message.document:
            file = update.message.document
            file_extension = file.file_name.split(".")[-1].lower()
        elif update.message.photo:
            file = update.message.photo[-1]  # Eng katta o'lchamdagi rasmni olish
            file_extension = "jpg"

        if not file or file_extension not in [
            "pdf",
            "docx",
            "doc",
            "jpg",
            "jpeg",
            "png",
        ]:
            await update.message.reply_text(
                "❌ Faqat PDF, DOCX yoki rasm formatidagi fayllarni yuborishingiz mumkin."
            )
            return

        # Faylni yuklab olish
        try:
            telegram_file = await file.get_file()
            file_path = f"tests/{user.id}_{file.file_id}.{file_extension}"
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            await telegram_file.download_to_drive(full_path)

            data = state.data
            data["file_path"] = file_path
            BotUtils.set_user_state(user, BotStates.CREATE_TEST_START_DAY, data)

            await update.message.reply_text(
                "3️⃣ Test boshlaniladigan kunni tanlang:",
                reply_markup=BotKeyboards.weekdays(),
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Faylni yuklashda xatolik: {str(e)}")

    @staticmethod
    async def create_test_start_day_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_START_DAY:
            return

        day = update.message.text.strip()

        if day not in [
            "Dushanba",
            "Seshanba",
            "Chorshanba",
            "Payshanba",
            "Juma",
            "Shanba",
            "Yakshanba",
        ]:
            await update.message.reply_text("❌ Iltimos, tugmalardan birini tanlang.")
            return

        data = state.data
        data["start_weekday"] = BotUtils.weekday_to_english(day)
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_START_TIME, data)

        await update.message.reply_text(
            "4️⃣ Test boshlaniladigan vaqtni tanlang:",
            reply_markup=BotKeyboards.time_slots(),
        )

    @staticmethod
    async def create_test_start_time_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_START_TIME:
            return

        time_str = update.message.text.strip()
        time_obj = BotUtils.format_time(time_str)

        if not time_obj:
            await update.message.reply_text(
                "❌ Noto'g'ri vaqt formati. Tugmalardan tanlang."
            )
            return

        data = state.data
        data["start_time"] = time_str
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_END_DAY, data)

        await update.message.reply_text(
            "5️⃣ Test tugaydigan kunni tanlang:", reply_markup=BotKeyboards.weekdays()
        )

    @staticmethod
    async def create_test_end_day_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Test tugash kuni handler"""
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_END_DAY:
            return

        day = update.message.text.strip()

        if day not in [
            "Dushanba",
            "Seshanba",
            "Chorshanba",
            "Payshanba",
            "Juma",
            "Shanba",
            "Yakshanba",
        ]:
            await update.message.reply_text("❌ Iltimos, tugmalardan birini tanlang.")
            return

        data = state.data
        data["end_weekday"] = BotUtils.weekday_to_english(day)
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_END_TIME, data)

        await update.message.reply_text(
            "6️⃣ Test tugaydigan vaqtni tanlang:", reply_markup=BotKeyboards.time_slots()
        )

    @staticmethod
    async def create_test_end_time_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Test tugash vaqti handler"""
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_END_TIME:
            return

        time_str = update.message.text.strip()
        time_obj = BotUtils.format_time(time_str)

        if not time_obj:
            await update.message.reply_text(
                "❌ Noto'g'ri vaqt formati. Tugmalardan tanlang."
            )
            return

        data = state.data
        data["end_time"] = time_str
        BotUtils.set_user_state(user, BotStates.CREATE_TEST_ANSWERS, data)

        await update.message.reply_text(
            "7️⃣ Test javoblarini kiriting:\n\n"
            "📌 <b>Format:</b> 1.A, 2.B, 3.C, 4.D, ...\n\n"
            "<i>Misol: 1.A, 2.C, 3.B, 4.D, 5.A</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=BotKeyboards.cancel(),
        )

    @staticmethod
    async def create_test_answers_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.CREATE_TEST_ANSWERS:
            return

        answers = update.message.text.strip()

        if not AnswerKey.validate_format(answers):
            await update.message.reply_text(
                "❌ Javoblar formati noto'g'ri!\n\n"
                "To'g'ri format: 1.A, 2.B, 3.C, ...\n"
                "Iltimos, qaytadan kiriting."
            )
            return

        try:
            data = state.data

            test = Test.objects.create(
                teacher=user,
                title=data["title"],
                file=data["file_path"],
                start_weekday=data["start_weekday"],
                start_time=BotUtils.format_time(data["start_time"]),
                end_weekday=data["end_weekday"],
                end_time=BotUtils.format_time(data["end_time"]),
                status="active",
            )

            parsed_answers = AnswerKey.parse_answers(answers)
            AnswerKey.objects.create(
                test=test, answers=answers, total_questions=len(parsed_answers)
            )

            await update.message.reply_text(
                f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                f"📝 Nomi: {test.title}\n"
                f"📊 Jami savollar: {len(parsed_answers)}\n"
                f"📅 Boshlanish: {data['start_weekday'].title()} {data['start_time']}\n"
                f"📅 Tugash: {data['end_weekday'].title()} {data['end_time']}",
                reply_markup=BotKeyboards.main_menu_teacher(),
            )

            BotUtils.clear_user_state(user)

        except Exception as e:
            await update.message.reply_text(
                f"❌ Testni yaratishda xatolik: {str(e)}\n\n"
                "Iltimos, qaytadan urinib ko'ring."
            )

    @staticmethod
    async def my_tests_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = User.objects.get(telegram_id=update.effective_user.id)

        tests = Test.objects.filter(teacher=user).order_by("-created_at")

        if not tests.exists():
            await update.message.reply_text(
                "📝 Sizda hali testlar yo'q.\n\n"
                "Yangi test yaratish uchun '➕ Yangi test' tugmasini bosing."
            )
            return

        tests_data = [{"id": t.id, "title": t.title} for t in tests]

        await update.message.reply_text(
            "📝 Sizning testlaringiz:",
            reply_markup=BotKeyboards.test_list_inline(tests_data),
        )

    @staticmethod
    async def available_tests_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Mavjud testlar (o'quvchi uchun)"""
        tests = Test.objects.filter(status="active").order_by("-created_at")

        if not tests.exists():
            await update.message.reply_text("📝 Hozirda faol testlar mavjud emas.")
            return

        tests_data = [{"id": t.id, "title": t.title} for t in tests]

        await update.message.reply_text(
            "📝 Mavjud testlar:", reply_markup=BotKeyboards.test_list_inline(tests_data)
        )

    @staticmethod
    async def submit_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Javoblarni yuborish"""
        user = User.objects.get(telegram_id=update.effective_user.id)
        state = BotUtils.get_user_state(user)

        if state.state != BotStates.SUBMITTING_ANSWERS:
            return

        answers = update.message.text.strip()
        test_id = state.data.get("test_id")

        if not AnswerKey.validate_format(answers):
            await update.message.reply_text(
                "❌ Javoblar formati noto'g'ri!\n\n"
                "To'g'ri format: 1.A, 2.B, 3.C, ...\n"
                "Iltimos, qaytadan kiriting."
            )
            return

        try:
            test = Test.objects.get(id=test_id)

            # Avval yuborgan javobini tekshirish
            if StudentAnswer.objects.filter(student=user, test=test).exists():
                await update.message.reply_text(
                    "❌ Siz bu testni allaqachon topshirgansiz!",
                    reply_markup=BotKeyboards.main_menu_student(),
                )
                BotUtils.clear_user_state(user)
                return

            student_answer = StudentAnswer.objects.create(
                student=user, test=test, answers=answers
            )
            student_answer.calculate_score()

            result_text = BotUtils.format_test_result(student_answer)

            await update.message.reply_text(
                result_text,
                parse_mode=ParseMode.HTML,
                reply_markup=BotKeyboards.main_menu_student(),
            )

            BotUtils.clear_user_state(user)

        except Test.DoesNotExist:
            await update.message.reply_text("❌ Test topilmadi.")
            BotUtils.clear_user_state(user)

    @staticmethod
    async def my_results_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim"""
        user = User.objects.get(telegram_id=update.effective_user.id)

        results = StudentAnswer.objects.filter(student=user).order_by("-submitted_at")

        if not results.exists():
            await update.message.reply_text("📊 Sizda hali natijalar yo'q.")
            return

        text = "📊 <b>Sizning natijalaringiz:</b>\n\n"

        for result in results:
            text += f"📝 {result.test.title}\n"
            text += f"✅ To'g'ri: {result.correct_count}\n"
            text += f"❌ Noto'g'ri: {result.incorrect_count}\n"
            text += f"📈 Foiz: {result.score_percentage:.2f}%\n"
            text += f"📅 Sana: {result.submitted_at.strftime('%d.%m.%Y %H:%M')}\n\n"

        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    @staticmethod
    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback query handler"""
        query = update.callback_query
        await query.answer()

        user = User.objects.get(telegram_id=update.effective_user.id)
        data = query.data

        if data.startswith("test_"):
            test_id = int(data.split("_")[1])
            test = Test.objects.get(id=test_id)

            test_info = f"📝 <b>{test.title}</b>\n\n"
            test_info += f"👨‍🏫 O'qituvchi: {test.teacher.full_name}\n"
            test_info += f"📊 Savollar soni: {test.answer_key.total_questions}\n"
            test_info += (
                f"📅 Boshlanish: {test.start_weekday.title()} {test.start_time}\n"
            )
            test_info += f"📅 Tugash: {test.end_weekday.title()} {test.end_time}\n"

            if user.is_teacher or user.is_admin:
                keyboard = BotKeyboards.test_actions_teacher(test_id)
            else:
                keyboard = BotKeyboards.test_actions_student(test_id)

            await query.edit_message_text(
                test_info, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )

        elif data.startswith("start_test_"):
            test_id = int(data.split("_")[2])

            BotUtils.set_user_state(
                user, BotStates.SUBMITTING_ANSWERS, {"test_id": test_id}
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✍️ Test boshlandi!\n\n"
                "Javoblaringizni quyidagi formatda yuboring:\n"
                "<b>1.A, 2.B, 3.C, 4.D, ...</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=BotKeyboards.cancel(),
            )

        elif data == "check_membership":
            is_member = await BotUtils.check_channel_membership(
                context.bot, user.telegram_id
            )

            if is_member:
                user.is_channel_member = True
                user.save()

                await query.edit_message_text(
                    "✅ A'zolik tasdiqlandi! Endi botdan foydalanishingiz mumkin.\n\n"
                    "/start ni bosing."
                )
            else:
                await query.answer(
                    "❌ Siz hali kanalga a'zo bo'lmagansiz!", show_alert=True
                )

    @staticmethod
    async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = User.objects.get(telegram_id=update.effective_user.id)
        BotUtils.clear_user_state(user)

        if user.is_admin:
            keyboard = BotKeyboards.main_menu_admin()
        elif user.is_teacher:
            keyboard = BotKeyboards.main_menu_teacher()
        else:
            keyboard = BotKeyboards.main_menu_student()

        await update.message.reply_text("❌ Bekor qilindi.", reply_markup=keyboard)

    @staticmethod
    async def unknown_message_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        try:
            user = User.objects.get(telegram_id=update.effective_user.id)
            state = BotUtils.get_user_state(user)

            if state.state in [
                BotStates.SUBMITTING_ANSWERS,
                BotStates.CREATE_TEST_ANSWERS,
            ]:
                return

            BotUtils.delete_message_safe(update, context)

        except User.DoesNotExist:
            pass

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
            ℹ️ <b>Bot haqida yordam</b>

            <b>O'quvchilar uchun:</b>
            • 📝 Mavjud testlar - Faol testlarni ko'rish
            • ✍️ Test ishlash - Javoblarni yuborish (1.A, 2.B, 3.C formatida)
            • 📊 Natijalarim - O'z natijalaringizni ko'rish

            <b>O'qituvchilar uchun:</b>
            • ➕ Yangi test - Yangi test yaratish
            • 📝 Mening testlarim - O'z testlaringizni boshqarish
            • 📊 Natijalar - O'quvchilar natijalarini ko'rish

            Qo'shimcha savol bo'lsa, admin bilan bog'laning.
                    """

        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
