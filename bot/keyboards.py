from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
)


class BotKeyboards:

    @staticmethod
    def phone_request():
        keyboard = [
            [KeyboardButton("📱 Telefon raqamimni yuborish", request_contact=True)]
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    @staticmethod
    def main_menu_admin():
        keyboard = [
            ["📊 Statistika", "👥 O'qituvchilar"],
            ["📢 Reklama", "🔗 Guruh/Kanel"],
            ["⚙️ Sozlamalar"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def main_menu_teacher():
        keyboard = [
            ["➕ Yangi test", "📝 Mening testlarim"],
            ["📊 Natijalar", "ℹ️ Qo'llanma"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def main_menu_student():
        """O'quvchi asosiy menyu"""
        keyboard = [
            ["📝 Mavjud testlar", "📊 Natijalarim"],
            ["📢 Reklama", "ℹ️ Qo'llanma"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def weekdays():
        keyboard = [
            ["Dushanba", "Seshanba", "Chorshanba"],
            ["Payshanba", "Juma"],
            ["Shanba", "Yakshanba"],
            ["🔙 Orqaga"],
        ]
        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    @staticmethod
    def time_slots():
        times = []
        for hour in range(7, 24):
            times.append(f"{hour:02d}:00")
            if hour < 23:
                times.append(f"{hour:02d}:30")

        keyboard = [times[i : i + 3] for i in range(0, len(times), 3)]
        keyboard.append(["🔙 Orqaga"])

        return ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )

    @staticmethod
    def cancel():
        keyboard = [["❌ Bekor qilish"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def back():
        keyboard = [["🔙 Orqaga"]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def test_list_inline(tests):
        keyboard = []
        for test in tests:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        test["title"], callback_data=f"test_{test['id']}"
                    )
                ]
            )
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def test_actions_teacher(test_id):
        keyboard = [
            [
                InlineKeyboardButton("📊 Statistika", callback_data=f"stats_{test_id}"),
                InlineKeyboardButton(
                    "📥 Natijalarni yuklab olish", callback_data=f"export_{test_id}"
                ),
            ],
            [
                InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_{test_id}"),
                InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{test_id}"),
            ],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_tests")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def test_actions_student(test_id):
        keyboard = [
            [
                InlineKeyboardButton(
                    "✍️ Testni boshlash", callback_data=f"start_test_{test_id}"
                )
            ],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_tests")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def channel_check(channel_url):
        keyboard = [
            [InlineKeyboardButton("� Kanalga o'tish", url=channel_url)],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_membership")],
        ]
        return InlineKeyboardMarkup(keyboard)
