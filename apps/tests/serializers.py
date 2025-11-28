from rest_framework import serializers
from .models import Test, AnswerKey, StudentAnswer
from apps.users.serializers import UserSerializer


class AnswerKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerKey
        fields = ["id", "test", "answers", "total_questions", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_answers(self, value):
        if not AnswerKey.validate_format(value):
            raise serializers.ValidationError(
                "Javoblar formati noto'g'ri. To'g'ri format: 1.A, 2.B, 3.C, ..."
            )
        return value


class TestSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    answer_key = AnswerKeySerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Test
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "title",
            "file",
            "start_weekday",
            "start_time",
            "end_weekday",
            "end_time",
            "status",
            "status_display",
            "answer_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TestCreateSerializer(serializers.ModelSerializer):
    answers = serializers.CharField(write_only=True)

    class Meta:
        model = Test
        fields = [
            "teacher",
            "title",
            "file",
            "start_weekday",
            "start_time",
            "end_weekday",
            "end_time",
            "answers",
        ]

    def validate_answers(self, value):
        if not AnswerKey.validate_format(value):
            raise serializers.ValidationError(
                "Javoblar formati noto'g'ri. To'g'ri format: 1.A, 2.B, 3.C, ..."
            )
        return value

    def create(self, validated_data):
        answers = validated_data.pop("answers")
        test = Test.objects.create(**validated_data)

        parsed_answers = AnswerKey.parse_answers(answers)
        AnswerKey.objects.create(
            test=test, answers=answers, total_questions=len(parsed_answers)
        )

        return test


class StudentAnswerSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    test_title = serializers.CharField(source="test.title", read_only=True)

    class Meta:
        model = StudentAnswer
        fields = [
            "id",
            "student",
            "student_name",
            "test",
            "test_title",
            "answers",
            "correct_count",
            "incorrect_count",
            "score_percentage",
            "wrong_questions",
            "submitted_at",
        ]
        read_only_fields = [
            "id",
            "correct_count",
            "incorrect_count",
            "score_percentage",
            "wrong_questions",
            "submitted_at",
        ]

    def validate(self, data):
        if StudentAnswer.objects.filter(
            student=data["student"], test=data["test"]
        ).exists():
            raise serializers.ValidationError("Siz bu testni allaqachon topshirgansiz!")

        if not AnswerKey.validate_format(data["answers"]):
            raise serializers.ValidationError(
                {
                    "answers": "Javoblar formati noto'g'ri. To'g'ri format: 1.A, 2.B, 3.C, ..."
                }
            )

        return data

    def create(self, validated_data):
        answer = StudentAnswer.objects.create(**validated_data)
        answer.calculate_score()
        return answer
