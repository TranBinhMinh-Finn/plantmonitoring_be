from rest_framework import permissions


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
