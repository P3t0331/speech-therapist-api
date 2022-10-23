"""
Views for the Meeting API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Meeting
from meeting import serializers


class MeetingViewSet(viewsets.ModelViewSet):
    """View for managing Meetings"""
    model = Meeting
    queryset = Meeting.objects.all()
    serializer_class = serializers.MeetingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Meetings for auth user"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new Meeting"""
        serializer.save(created_by=self.request.user)
