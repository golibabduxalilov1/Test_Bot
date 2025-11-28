from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg
from django.utils import timezone
from .models import Test, StudentAnswer, Weekday
from .serializers import TestSerializer, TestCreateSerializer, StudentAnswerSerializer
from apps.users.permissions import IsTeacherOrAdmin, IsStudent, IsOwnerOrAdmin


class TestListView(generics.ListAPIView):

    serializer_class = TestSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return Test.objects.all()
        elif user.is_teacher:
            return Test.objects.filter(teacher=user)
        else:
            return Test.objects.filter(status="active")


class TestCreateView(generics.CreateAPIView):

    queryset = Test.objects.all()
    serializer_class = TestCreateSerializer
    permission_classes = [IsTeacherOrAdmin]


class TestDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsOwnerOrAdmin]


class ActiveTestsView(generics.ListAPIView):

    serializer_class = TestSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        current_time = timezone.now()
        current_weekday = current_time.strftime("%A").lower()

        return Test.objects.filter(
            status="active",
            start_weekday__lte=current_weekday,
            end_weekday__gte=current_weekday,
        )


class StudentAnswerCreateView(generics.CreateAPIView):
    """O'quvchi javobini yuboris"""

    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsStudent]

    def create(self, request, *args, **kwargs):
        test_id = request.data.get("test")

        try:
            test = Test.objects.get(id=test_id)

            if test.status != "active":
                return Response(
                    {"error": "Bu test faol emas"}, status=status.HTTP_400_BAD_REQUEST
                )

            current_time = timezone.now()
            current_weekday = current_time.strftime("%A").lower()

            weekday_order = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }

            current_day_num = weekday_order.get(current_weekday, 0)
            start_day_num = weekday_order.get(test.start_weekday, 0)
            end_day_num = weekday_order.get(test.end_weekday, 6)

            if not (start_day_num <= current_day_num <= end_day_num):
                return Response(
                    {"error": "Test vaqti hali boshlanmagan yoki tugagan"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Test.DoesNotExist:
            return Response(
                {"error": "Test topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )

        return super().create(request, *args, **kwargs)


class StudentAnswerListView(generics.ListAPIView):

    serializer_class = StudentAnswerSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_admin or user.is_teacher:
            test_id = self.request.query_params.get("test_id")
            if test_id:
                return StudentAnswer.objects.filter(test_id=test_id)
            return StudentAnswer.objects.all()
        else:
            # O'quvchi faqat o'z javoblarini ko'radi
            return StudentAnswer.objects.filter(student=user)


class TestStatisticsView(APIView):

    permission_classes = [IsTeacherOrAdmin]

    def get(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)

            if not request.user.is_admin and test.teacher != request.user:
                return Response(
                    {"error": "Ruxsat berilmagan"}, status=status.HTTP_403_FORBIDDEN
                )

            answers = StudentAnswer.objects.filter(test=test)

            statistics = {
                "test_title": test.title,
                "total_students": answers.count(),
                "average_score": answers.aggregate(Avg("score_percentage"))[
                    "score_percentage__avg"
                ]
                or 0,
                "highest_score": answers.order_by("-score_percentage").first(),
                "lowest_score": answers.order_by("score_percentage").first(),
                "results": StudentAnswerSerializer(answers, many=True).data,
            }

            return Response(statistics)

        except Test.DoesNotExist:
            return Response(
                {"error": "Test topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )


class MyTestsView(generics.ListAPIView):

    serializer_class = TestSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return Test.objects.filter(teacher=self.request.user)
