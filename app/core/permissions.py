"""
Custom permissions for Speech Therapist
"""
from rest_framework import permissions


class IsTherapist(permissions.BasePermission):
    """
    Permission that only allows therapists to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_therapist


class IsOwnerOfObject(permissions.BasePermission):
    """
    Permission that only allows the owner of the object to access the view.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsPatientAssignedToTherapist(permissions.BasePermission):
    """
    Permission that only allows therapists to modify the fields that are their patients.
    """

    def has_object_permission(self, request, view, obj):
        return obj.assignment_active and obj.assigned_to == request.user


class IsTaskResultMyPatient(permissions.BasePermission):
    """
    Permission that only allows therapists to access the view for task results that are for their patients.
    """

    def has_object_permission(self, request, view, obj):
        patient = obj.answered_by
        return patient.assignment_active and patient.assigned_to == request.user
