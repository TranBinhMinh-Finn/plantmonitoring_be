from plantmon.models import CustomUser, Device, DeviceReadings
from rest_framework import permissions
from plantmon.serializers import UserAuthSerializer, UserDetailSerializer, DeviceSerializer, DeviceReadingsSerializer
from rest_framework import generics
from .permissions import IsOwner, IsEditingSelf, IsDeviceOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import manual_watering, update_watering_mode


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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        update_watering_mode.delay(serializer.data)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


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


class DeviceManualWatering(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]
    lookup_url_kwarg = "device"

    def put(self, request, device, format=None):
        manual_watering.delay(device)
        return Response("Command Received")
