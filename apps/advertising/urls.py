from django.urls import path
from .views import (
    AdvertisementListView,
    AdvertisementCreateView,
    AdvertisementDetailView,
    ActiveAdvertisementsView,
)

app_name = "advertising"

urlpatterns = [
    path("", AdvertisementListView.as_view(), name="ad-list"),
    path("create/", AdvertisementCreateView.as_view(), name="ad-create"),
    path("<int:pk>/", AdvertisementDetailView.as_view(), name="ad-detail"),
    path("active/", ActiveAdvertisementsView.as_view(), name="active-ads"),
]
