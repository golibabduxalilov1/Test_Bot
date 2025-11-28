from django.urls import path
from .views import (
    GroupChannelListView,
    GroupChannelCreateView,
    GroupChannelDetailView,
    MandatoryChannelsView,
)

app_name = "channels"

urlpatterns = [
    path("", GroupChannelListView.as_view(), name="channel-list"),
    path("create/", GroupChannelCreateView.as_view(), name="channel-create"),
    path("<int:pk>/", GroupChannelDetailView.as_view(), name="channel-detail"),
    path("mandatory/", MandatoryChannelsView.as_view(), name="mandatory-channels"),
]
