from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GroupChannel
from .serializers import GroupChannelSerializer
from apps.users.permissions import IsAdmin


class GroupChannelListView(generics.ListAPIView):

    queryset = GroupChannel.objects.filter(is_active=True)
    serializer_class = GroupChannelSerializer
    permission_classes = [IsAdmin]


class GroupChannelCreateView(generics.CreateAPIView):

    queryset = GroupChannel.objects.all()
    serializer_class = GroupChannelSerializer
    permission_classes = [IsAdmin]


class GroupChannelDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = GroupChannel.objects.all()
    serializer_class = GroupChannelSerializer
    permission_classes = [IsAdmin]


class MandatoryChannelsView(APIView):

    def get(self, request):
        channels = GroupChannel.objects.filter(is_active=True, is_mandatory=True)
        serializer = GroupChannelSerializer(channels, many=True)
        return Response(serializer.data)
