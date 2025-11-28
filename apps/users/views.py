from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from .models import User, UserRole, BotState
from .serializers import UserSerializer, UserCreateSerializer, BotStateSerializer
from .permissions import IsAdmin


class UserListView(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["role", "is_blocked"]
    search_fields = ["full_name", "username", "phone_number"]


class UserDetailView(generics.RetrieveUpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Foydalanuvchi faqat o'z ma'lumotlarini ko'rishi mumkin (admin bundan mustasno)
        if self.request.user.is_admin:
            return super().get_object()
        return self.request.user


class UserCreateView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class PromoteToTeacherView(APIView):

    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)

            if user.role == UserRole.ADMIN:
                return Response(
                    {"error": "Adminni o'qituvchi qila olmaysiz"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.role = UserRole.TEACHER
            user.save()

            return Response(
                {"message": f"{user.full_name} o'qituvchi qilib tayinlandi"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )


class RemoveTeacherView(APIView):

    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role=UserRole.TEACHER)
            user.role = UserRole.STUDENT
            user.save()

            return Response(
                {"message": f"{user.full_name} oddiy foydalanuvchi qilindi"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "O'qituvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )


class TeachersListView(generics.ListAPIView):

    queryset = User.objects.filter(role=UserRole.TEACHER)
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class BotStateView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
            bot_state, _ = BotState.objects.get_or_create(user=user)
            serializer = BotStateSerializer(bot_state)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
            bot_state, _ = BotState.objects.get_or_create(user=user)

            bot_state.state = request.data.get("state", bot_state.state)
            bot_state.data = request.data.get("data", bot_state.data)
            bot_state.save()

            serializer = BotStateSerializer(bot_state)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )
