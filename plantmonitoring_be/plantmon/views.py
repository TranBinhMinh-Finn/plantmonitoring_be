from plantmon.models import CustomUser, Device, DeviceReadings
from rest_framework import permissions
from plantmon.serializers import UserAuthSerializer, UserDetailSerializer, DeviceSerializer, DeviceReadingsSerializer
from rest_framework import generics
from .permissions import IsOwner, IsEditingSelf, IsDeviceOwner


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
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class DeviceReadingsList(generics.ListAPIView):
    serializer_class = DeviceReadingsSerializer
    lookup_url_kwarg = "device"
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]

    def get_queryset(self):
        queryset = DeviceReadings.objects.all()
        device = self.kwargs.get(self.lookup_url_kwarg)
        if device is not None:
            queryset = queryset.filter(device=device)
        return queryset
