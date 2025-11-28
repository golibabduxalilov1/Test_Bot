from telegram.ext.filters import MessageFilter
from apps.users.models import User, UserRole


class AdminFilter(MessageFilter):
    async def filter(self, message):
        try:
            user = User.objects.get(telegram_id=message.from_user.id)
            return user.role == UserRole.ADMIN
        except User.DoesNotExist:
            return False


class TeacherFilter(MessageFilter):
    async def filter(self, message):
        try:
            user = User.objects.get(telegram_id=message.from_user.id)
            return user.role == UserRole.TEACHER
        except User.DoesNotExist:
            return False


class StudentFilter(MessageFilter):
    async def filter(self, message):
        try:
            user = User.objects.get(telegram_id=message.from_user.id)
            return user.role == UserRole.STUDENT
        except User.DoesNotExist:
            return False


admin_filter = AdminFilter()
teacher_filter = TeacherFilter()
student_filter = StudentFilter()
