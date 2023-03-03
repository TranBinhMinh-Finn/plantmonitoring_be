from rest_framework import permissions
from .models import Device


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsEditingSelf(permissions.BasePermission):
    """
    Custom permission to only allow the object itself to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsDeviceOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        device_id = view.kwargs.get(view.lookup_url_kwarg)
        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            return False
        return device.owner == request.user
