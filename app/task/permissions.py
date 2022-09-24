"""
Permissions for task API
"""
from rest_framework import permissions


class IsTherapist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_therapist


class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
