from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Test, AnswerKey, StudentAnswer


@admin.register(Test)
class TestAdmin(ModelAdmin):

    list_display = ("teacher", "title")


@admin.register(AnswerKey)
class AnswerKeyAdmin(ModelAdmin):

    list_display = ("test", "total_questions")


@admin.register(StudentAnswer)
class AnswerKeyAdmin(ModelAdmin):

    list_display = ("student", "correct_count")
