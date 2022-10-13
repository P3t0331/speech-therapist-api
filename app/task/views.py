"""
Views for the Task API
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from task.permissions import IsTherapist, IsOwnerOfObject
from core.models import Task, BasicChoice, Tag, TaskResult
from task import serializers


def check_permissions(self):
    if self.action == 'create':
        composed_perm = IsAuthenticated & IsTherapist
        return [composed_perm()]
    if self.action == 'destroy' or self.action == 'update' \
       or self.action == 'partial_update':
        composed_perm = IsAuthenticated & IsTherapist & IsOwnerOfObject
        return [composed_perm()]


class TaskViewSet(viewsets.ModelViewSet):
    """View for manage Task APIs"""
    serializer_class = serializers.TaskDetailSerializer
    queryset = Task.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = Task

    def get_queryset(self):
        """Retrieve Tasks for auth user"""
        queryset = self.queryset
        return queryset.order_by('-id').distinct()

    def get_permissions(self):
        perm = check_permissions(self)
        if perm is not None:
            return perm
        return super().get_permissions()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.TaskSerializer
        elif self.action == 'assign_task':
            return serializers.AssignTaskSerializer
        elif self.action == 'get_random_task':
            return serializers.RandomTaskSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Task"""
        serializer.save(created_by=self.request.user)

    @action(methods=['PATCH'], detail=True, url_path='assign_task')
    def assign_task(self, request, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='get_random_task')
    def get_random_task(self, request, pk=None):
        task = Task.objects.filter(created_by=1).order_by('?').first()
        serializer = self.get_serializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasicChoiceViewSet(viewsets.ModelViewSet):
    """View for managing Basic Choices APIs"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BasicChoiceSerializer
    queryset = BasicChoice.objects.all()

    def get_queryset(self):
        return self.queryset.order_by('-id').distinct()

    def get_permissions(self):
        perm = check_permissions(self)
        if perm is not None:
            return perm
        return super().get_permissions()

    def perform_create(self, serializer):
        """Create a new BasicChoice"""
        serializer.save(created_by=self.request.user)


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TaskResultViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """View for creating task results"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = TaskResult.objects.all()
    serializer_class = serializers.TaskDetailResultSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.order_by('-id').distinct()

    def perform_create(self, serializer):
        serializer.save(answered_by=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.TaskResultSerializer
        return self.serializer_class
