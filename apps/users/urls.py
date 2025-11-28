from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    UserCreateView,
    PromoteToTeacherView,
    RemoveTeacherView,
    TeachersListView,
    BotStateView,
)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("teachers/", TeachersListView.as_view(), name="teachers-list"),
    path(
        "<int:user_id>/promote/", PromoteToTeacherView.as_view(), name="promote-teacher"
    ),
    path("<int:user_id>/remove/", RemoveTeacherView.as_view(), name="remove-teacher"),
    path("state/<int:telegram_id>/", BotStateView.as_view(), name="bot-state"),
]
