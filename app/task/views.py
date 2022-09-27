"""
Views for the Task API
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from task.permissions import IsTherapist, IsOwnerOfObject
from core.models import Task, Question, BasicChoice
from task import serializers


class TaskViewSet(viewsets.ModelViewSet):
    """View for manage Task APIs"""
    serializer_class = serializers.TaskSerializer
    queryset = Task.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tasks for auth user"""
        queryset = self.queryset
        return queryset.order_by('-id').distinct()

    def get_permissions(self):
        if self.action == 'create':
            composed_perm = IsAuthenticated & IsTherapist
            return [composed_perm()]
        if self.action == 'destroy' or self.action == 'update' \
           or self.action == 'partial_update':
            composed_perm = IsAuthenticated & IsTherapist & IsOwnerOfObject
            return [composed_perm()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Create a new Task"""
        serializer.save(created_by=self.request.user)


class QuestionsViewSet(mixins.DestroyModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """View for managing Question APIs"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.QuestionSerializer
    queryset = Question.objects.all()

    def get_queryset(self):
        return self.queryset.order_by('-id').distinct()


class BasicChoiceViewSet(viewsets.ModelViewSet):
    """View for managing Basic Choices APIs"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BasicChoiceSerializer
    queryset = BasicChoice.objects.all()

    def get_queryset(self):
        return self.queryset.order_by('-id').distinct()
