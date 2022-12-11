"""
Views for the Task API
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone

from core.permissions import (
    IsTherapist,
    IsOwnerOfObject,
    IsTaskResultMyPatient,
)
from core.models import Task, BasicChoice, Tag, TaskResult
from task import serializers


def str_to_bool(s):
    """
    Convert a string to a boolean value.

    `s`: The string to convert
    `@return`: `True` if the string is true, `False` otherwise
    """
    return s == "true"


def check_permissions(self):
    """
    This function checks the permission for different actions in the view

    `@param self`: instance of the view
    `@return`: list of permission class instances
    """
    if self.action == "create":
        composed_perm = IsAuthenticated & IsTherapist
        return [composed_perm()]
    if (
        self.action == "destroy"
        or self.action == "update"
        or self.action == "partial_update"
    ):
        composed_perm = IsAuthenticated & IsTherapist & IsOwnerOfObject
        return [composed_perm()]


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "default",
                OpenApiTypes.BOOL,
                enum=[True, False],
                description="Filter to show only default tasks",
            ),
            OpenApiParameter(
                "custom",
                OpenApiTypes.BOOL,
                enum=[True, False],
                description="Filter to show only custom tasks",
            ),
            OpenApiParameter(
                "generated",
                OpenApiTypes.BOOL,
                enum=[True, False],
                description="Filter to show only generated tasks",
            ),
        ]
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                "task_type",
                OpenApiTypes.STR,
                enum=[
                    "Connect_Pairs_Text-Image",
                    "Connect_Pairs_Text-Text",
                    "Four_Choices_Image-Texts",
                    "Four_Choices_Text-Images",
                ],
                description="Get questions based on this task type",
            )
        ]
    ),
    create=extend_schema(
        parameters=[
            OpenApiParameter(
                "task_type",
                OpenApiTypes.STR,
                enum=[
                    "Connect_Pairs_Text-Image",
                    "Connect_Pairs_Text-Text",
                    "Four_Choices_Image-Texts",
                    "Four_Choices_Text-Images",
                ],
                description="POST questions based on this task type",
            )
        ]
    ),
    partial_update=extend_schema(
        parameters=[
            OpenApiParameter(
                "task_type",
                OpenApiTypes.STR,
                enum=[
                    "Connect_Pairs_Text-Image",
                    "Connect_Pairs_Text-Text",
                    "Four_Choices_Image-Texts",
                    "Four_Choices_Text-Images",
                ],
                description="PATCH questions based on this task type",
            )
        ]
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """View for manage Task APIs"""

    serializer_class = serializers.ConnectPairsTaskDetailSerializer
    queryset = Task.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = Task

    def get_queryset(self):
        """
        Retrieve Tasks for authenticated user.
        The returned queryset can be filtered based on
        the following query parameters:
            - default: If set to True, only tasks created by
            the default user will be included in the queryset.
            - custom: If set to True, only tasks that are marked as custom
            will be included in the queryset.
            - generated: If set to True, only tasks that are not created by the
            default user and are not marked as custom
            will be included in the queryset.
        If no query parameters are provided, the queryset will not be
        filtered and will be ordered by the task id in descending order.
        """
        queryset = self.queryset.none()
        queryset1 = self.queryset
        queryset2 = self.queryset
        queryset3 = self.queryset
        default_param = str_to_bool(
            self.request.query_params.get("default", False)
        )
        custom_param = str_to_bool(
            self.request.query_params.get("custom", False)
        )
        generated_param = str_to_bool(
            self.request.query_params.get("generated", False)
        )
        if default_param:
            queryset1 = self.queryset.filter(created_by=1)
            queryset = queryset | queryset1

        if custom_param:
            queryset2 = self.queryset.filter(is_custom=1)
            queryset = queryset | queryset2

        if generated_param:
            queryset3 = self.queryset.exclude(created_by=1).filter(is_custom=0)
            queryset = queryset | queryset3

        if not default_param and not custom_param and not generated_param:
            return self.queryset.order_by("-id").distinct()
        return queryset.order_by("-id").distinct()

    def get_permissions(self):
        """
        Check permissions for the request. If the user does not
        have the required permissions, return a permission denied error.
        """
        perm = check_permissions(self)
        if perm is not None:
            return perm
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Return the appropriate serializer class for the request
        based on the `task_type` query parameter.
        If the `task_type` query parameter is not provided,
        the default `TaskDetailSerializer` will be used.
        The possible values for the `task_type` query parameter
        and the corresponding serializer classes are:
            - Connect_Pairs_Text-Image: `ConnectPairsTaskDetailSerializer`
            - Connect_Pairs_Text-Text: `ConnectPairsTaskDetailSerializer`
            - Four_Choices_Image-Texts: `FourChoicesTaskDetailSerializer`
            - Four_Choices_Text-Images: `FourChoicesTaskDetailSerializer`
        """
        task_param = self.request.query_params.get("task_type", "invalid")
        if self.action == "list":
            return serializers.TaskSerializer
        elif self.action == "assign_task":
            return serializers.AssignTaskSerializer
        elif self.action == "get_random_task":
            return serializers.RandomTaskSerializer
        elif (
            task_param == "Connect_Pairs_Text-Text"
            or task_param == "Connect_Pairs_Text-Image"
        ):
            return serializers.ConnectPairsTaskDetailSerializer
        elif (
            task_param == "Four_Choices_Image-Texts"
            or task_param == "Four_Choices_Text-Images"
        ):
            return serializers.FourChoicesTaskDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Create a new Task.
        The created_by field of the Task will be set to the authenticated
        user and the is_custom field will be set to True
        if the serializer class is either `CustomTaskDetailSerializer`
        or `FourChoicesTaskDetailSerializer`.
        """
        if (
            self.get_serializer_class()
            == serializers.ConnectPairsTaskDetailSerializer
            or self.get_serializer_class()
            == serializers.FourChoicesTaskDetailSerializer
        ):
            serializer.save(created_by=self.request.user, is_custom=True)
        else:
            serializer.save(created_by=self.request.user)

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="assign_task",
        permission_classes=[IsAuthenticated, IsTherapist],
    )
    def assign_task(self, request, pk=None):
        """
        Assign the Task with the given primary key to a user.
        Only users with the `IsTherapist` permission can access this action.
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="get_random_task")
    def get_random_task(self, request, pk=None):
        """
        Return a random Task created by the default user.
        """
        task = Task.objects.filter(created_by=1).order_by("?").first()
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
        """
        Retrieve the BasicChoices in the database, ordered by the id
        in descending order.
        """
        return self.queryset.order_by("-id").distinct()

    def get_permissions(self):
        """
        Check permissions for the request. If the user does not have the
        required permissions, return a permission denied error.
        """
        perm = check_permissions(self)
        if perm is not None:
            return perm
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Create a new BasicChoice.
        The created_by field of the BasicChoice will be set to the
        authenticated user.
        """
        serializer.save(created_by=self.request.user)


class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Manage tags in the database"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        """
        Retrieve the tags in the database that are associated with the
        authenticated user, ordered by the name in descending order.
        """
        return self.queryset.filter(
            user=self.request.user
        ).order_by("-name").distinct()

    def get_permissions(self):
        """
        Check permissions for the request. If the user does not have the
        required permissions, return a permission denied error.
        """
        perm = check_permissions(self)
        if perm is not None:
            return perm
        return super().get_permissions()


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                "task_type",
                OpenApiTypes.STR,
                enum=[
                    "Connect_Pairs_Text-Image",
                    "Connect_Pairs_Text-Text",
                    "Four_Choices_Image-Texts",
                    "Four_Choices_Text-Images",
                ],
                description="Get questions based on this task type",
            )
        ]
    ),
    create=extend_schema(
        parameters=[
            OpenApiParameter(
                "task_type",
                OpenApiTypes.STR,
                enum=[
                    "Connect_Pairs_Text-Image",
                    "Connect_Pairs_Text-Text",
                    "Four_Choices_Image-Texts",
                    "Four_Choices_Text-Images",
                ],
                description="POST questions based on this task type",
            )
        ]
    ),
)
class TaskResultViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """View for creating task results"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = TaskResult.objects.all()
    serializer_class = serializers.TaskDetailResultSerializer

    def get_serializer_class(self):
        """
        Return the appropriate serializer class for the request based on the
        `task_type` query parameter.
        If the `task_type` query parameter is not provided, the default
        `TaskDetailResultSerializer` will be used.
        The possible values for the `task_type` query parameter and the
        corresponding serializer classes are:
            - Four_Choices_Image-Texts: `TaskDetailFourChoiceResultSerializer`
            - Four_Choices_Text-Images: `TaskDetailFourChoiceResultSerializer`
        """
        task_param = self.request.query_params.get("task_type", "invalid")
        if self.action == "list":
            return serializers.TaskResultSerializer
        if (
            task_param == "Four_Choices_Image-Texts"
            or task_param == "Four_Choices_Text-Images"
        ):
            return serializers.TaskDetailFourChoiceResultSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        """
        Check permissions for the request.
        If the request is a `destroy` or `retrieve` action, the user must have
        the `IsAuthenticated`, `IsTherapist`, and `IsTaskResultMyPatient`
        permissions.
        Otherwise, return the default permissions.
        """
        if self.action == "destroy" or self.action == "retrieve":
            composed_perm = IsAuthenticated & IsTherapist &\
                IsTaskResultMyPatient
            return [composed_perm()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Retrieve the TaskResults in the database, ordered by the id in
        descending order.
        """
        queryset = self.queryset
        return queryset.order_by("-id").distinct()

    def perform_create(self, serializer):
        """
        Create a new TaskResult.
        The `answered_by` field of the `TaskResult` will be set to the
        authenticated user.
        The `date_created` field of the `TaskResult` will be set to the
        current time.
        The `last_result_posted` field of the authenticated user will be set
        to the current time.
        """
        serializer.save(
            answered_by=self.request.user,
            date_created=timezone.now()
        )
        self.request.user.last_result_posted = timezone.now()
        self.request.user.save()
