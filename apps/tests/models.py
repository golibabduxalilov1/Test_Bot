from django.db import models
from django.core.validators import FileExtensionValidator
from apps.users.models import User
import re


class Weekday(models.TextChoices):

    MONDAY = "monday", "Dushanba"
    TUESDAY = "tuesday", "Seshanba"
    WEDNESDAY = "wednesday", "Chorshanba"
    THURSDAY = "thursday", "Payshanba"
    FRIDAY = "friday", "Juma"
    SATURDAY = "saturday", "Shanba"
    SUNDAY = "sunday", "Yakshanba"


class Test(models.Model):

    STATUS_CHOICES = [
        ("pending", "Kutilmoqda"),
        ("active", "Faol"),
        ("completed", "Tugagan"),
        ("cancelled", "Bekor qilingan"),
    ]

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tests",
        limit_choices_to={"role": "teacher"},
        verbose_name="O'qituvchi",
    )
    title = models.CharField(max_length=255, verbose_name="Test nomi")
    file = models.FileField(
        upload_to="tests/%Y/%m/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "docx", "doc", "jpg", "jpeg", "png"]
            )
        ],
        verbose_name="Test fayli",
    )
    start_weekday = models.CharField(
        max_length=20, choices=Weekday.choices, verbose_name="Boshlanish kuni"
    )
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_weekday = models.CharField(
        max_length=20, choices=Weekday.choices, verbose_name="Tugash kuni"
    )
    end_time = models.TimeField(verbose_name="Tugash vaqti")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Holat"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        db_table = "tests"
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AnswerKey(models.Model):

    test = models.OneToOneField(
        Test, on_delete=models.CASCADE, related_name="answer_key", verbose_name="Test"
    )
    answers = models.TextField(
        verbose_name="Javoblar", help_text="Format: 1.A, 2.B, 3.C, ..."
    )
    total_questions = models.PositiveIntegerField(verbose_name="Jami savollar soni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        db_table = "answer_keys"
        verbose_name = "Javoblar kaliti"
        verbose_name_plural = "Javoblar kalitlari"

    def __str__(self):
        return f"{self.test.title} - Kaliti"

    @staticmethod
    def parse_answers(answer_string):
        """
        Javoblarni parse qilish
        Input: "1.A, 2.B, 3.C, 4.D"
        Output: {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        """
        pattern = r"(\d+)\.([A-Da-d])"
        matches = re.findall(pattern, answer_string)
        return {int(num): letter.upper() for num, letter in matches}

    @staticmethod
    def validate_format(answer_string):
        pattern = r"^(\d+\.[A-Da-d],?\s*)+$"
        return bool(re.match(pattern, answer_string.strip()))


class StudentAnswer(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_answers",
        limit_choices_to={"role": "student"},
        verbose_name="O'quvchi",
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="student_answers",
        verbose_name="Test",
    )
    answers = models.TextField(verbose_name="Javoblar")
    correct_count = models.PositiveIntegerField(
        default=0, verbose_name="To'g'ri javoblar"
    )
    incorrect_count = models.PositiveIntegerField(
        default=0, verbose_name="Noto'g'ri javoblar"
    )
    score_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name="Foiz"
    )
    wrong_questions = models.JSONField(
        default=list, blank=True, verbose_name="Xato savollar"
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yuborilgan vaqt"
    )

    class Meta:
        db_table = "student_answers"
        verbose_name = "O'quvchi javobi"
        verbose_name_plural = "O'quvchi javoblari"
        unique_together = ["student", "test"]
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.test.title}"

    def calculate_score(self):
        student_answers = AnswerKey.parse_answers(self.answers)
        correct_answers = AnswerKey.parse_answers(self.test.answer_key.answers)

        self.correct_count = 0
        self.wrong_questions = []

        for question_num, student_answer in student_answers.items():
            if question_num in correct_answers:
                if student_answer == correct_answers[question_num]:
                    self.correct_count += 1
                else:
                    self.wrong_questions.append(
                        {
                            "question": question_num,
                            "student_answer": student_answer,
                            "correct_answer": correct_answers[question_num],
                        }
                    )

        total = self.test.answer_key.total_questions
        self.incorrect_count = total - self.correct_count
        self.score_percentage = (self.correct_count / total * 100) if total > 0 else 0
        self.save()
