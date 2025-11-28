from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Advertisement
from .serializers import AdvertisementSerializer
from apps.users.permissions import IsAdmin


class AdvertisementListView(generics.ListAPIView):

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAdmin]


class AdvertisementCreateView(generics.CreateAPIView):

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAdmin]


class AdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAdmin]


class ActiveAdvertisementsView(APIView):

    def get(self, request):
        user = request.user

        if user.is_student:
            ads = Advertisement.objects.filter(is_active=True, show_to_students=True)
        elif user.is_teacher:
            ads = Advertisement.objects.filter(is_active=True, show_to_teachers=True)
        else:
            ads = Advertisement.objects.filter(is_active=True)

        serializer = AdvertisementSerializer(ads, many=True)
        return Response(serializer.data)
