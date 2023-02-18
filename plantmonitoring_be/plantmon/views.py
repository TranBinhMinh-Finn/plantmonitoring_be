from plantmon.models import CustomUser, Device
from rest_framework import permissions
from plantmon.serializers import UserAuthSerializer, UserDetailSerializer, DeviceSerializer
from rest_framework import generics
from .permissions import IsOwner, IsEditingSelf


class UserDetail(generics.RetrieveDestroyAPIView):
    """
    API endpoint that allows users to get or destrot their account
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditingSelf]


class UserUpdate(generics.UpdateAPIView):
    """
    API endpoint that allows users to update their info
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditingSelf]


class UserRegister(generics.CreateAPIView):
    """
    API endpoint that allows quests to register
    """
    serializer_class = UserAuthSerializer


class DeviceCreate(generics.CreateAPIView):
    """
    API endpoint that allows users to add their devices
    """
    serializer_class = DeviceSerializer


class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
