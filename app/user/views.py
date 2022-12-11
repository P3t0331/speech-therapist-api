"""
Views for the user api
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    UserTherapistSerializer,
    AssignTherapistSerializer,
    WaitingToLinkSerializer,
    UpdateNoteSerializer,
    PatientViewSerializer,
    UpdateDiagnosisSerializer,
)
from user.serializers import AuthTokenSerializer
from core.models import User, Meeting
from core.permissions import IsTherapist, IsPatientAssignedToTherapist

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


class CreatePatientView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTherapistView(generics.CreateAPIView):
    """Create a new therapist in the system"""

    serializer_class = UserTherapistSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user


class ManagerUserTherapistView(generics.RetrieveUpdateAPIView):
    """Manage authenticated therapist user"""

    serializer_class = UserTherapistSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsTherapist]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "linked_only",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Filter users to list only linked patients",
            )
        ]
    )
)
class ListPatientUserView(generics.ListAPIView):
    """
    View for listing patient users.
    """

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated & IsTherapist]

    def get_queryset(self):
        """
        This view will return a list of all the patient users.
        If the 'linked_only' query parameter is provided with a value of 1,
        the view will return only patients that are linked to the authenticated therapist.
        """
        queryset = User.objects.all().filter(is_therapist=False)
        linked_only = bool(int(self.request.query_params.get("linked_only", 0)))
        if linked_only:
            queryset = queryset.filter(
                assigned_to=self.request.user, assignment_active=True
            )
        return queryset


class ListTherapistUserView(generics.ListAPIView):
    """
    View for listing therapist users.
    """

    serializer_class = UserTherapistSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view will return a list of all the therapist users.
        """
        queryset = User.objects.all().filter(is_therapist=True)
        return queryset


class GetPatientUserView(generics.RetrieveAPIView):
    """
    View for retrieving a patient user.
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [
        permissions.IsAuthenticated & IsPatientAssignedToTherapist & IsTherapist
    ]
    queryset = User.objects.all()
    serializer_class = PatientViewSerializer


class GetTherapistUserView(generics.RetrieveAPIView):
    """
    View for retrieving a therapist user.
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserTherapistSerializer


class AssignTherapistView(generics.UpdateAPIView):
    """View for linking to therapists"""

    http_method_names = ["patch"]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = AssignTherapistSerializer

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user


class PatientsWaitingToLinkView(generics.ListAPIView):
    """View for listing patients that are waiting to be linked"""

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WaitingToLinkSerializer

    def get_queryset(self):
        queryset = (
            User.objects.all()
            .exclude(assigned_to__isnull=True)
            .filter(assignment_active=False)
        )
        queryset = (
            queryset.filter(assigned_to=self.request.user).order_by("-id").distinct()
        )
        return queryset


class GenericLinkView(generics.UpdateAPIView):
    """Generic view for links"""

    http_method_names = ["patch"]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated & IsTherapist]
    lookup_field = "pk"

    queryset = User.objects.all()
    serializer_class = WaitingToLinkSerializer


class AcceptLinkView(GenericLinkView):
    """View for accepting link to therapists"""

    def update(self, request, *args, **kwargs):
        request_id = int(self.kwargs["pk"])
        User.objects.filter(id=request_id).update(assignment_active=True)
        return super().update(request, *args, **kwargs)


class RejectLinkView(GenericLinkView):
    """View for rejecting link to therapists"""

    def update(self, request, *args, **kwargs):
        request_id = int(self.kwargs["pk"])
        User.objects.filter(id=request_id).update(
            assigned_to="", assignment_active=False
        )
        return super().update(request, *args, **kwargs)


class UpdateNoteView(generics.UpdateAPIView):
    """
    View for adding notes to patients.
    """

    http_method_names = ["patch"]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated & IsTherapist]
    queryset = User.objects.all()
    serializer_class = UpdateNoteSerializer


class UpdateDiagnosisView(generics.UpdateAPIView):
    """
    View for adding diagnoses to patients.
    """

    http_method_names = ["patch"]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated & IsTherapist]
    queryset = User.objects.all()
    serializer_class = UpdateDiagnosisSerializer


class TherapistUnlinkView(GenericLinkView):
    """
    View for therapist for unassigning a patient.
    """

    def update(self, request, *args, **kwargs):
        request_id = int(self.kwargs["pk"])
        user = User.objects.filter(id=request_id).first()
        user.assigned_to = None
        user.assignment_active = False
        user.assigned_tasks.clear()
        Meeting.objects.all().filter(assigned_patient=user).delete()
        user.save()
        return super().update(request, *args, **kwargs)


class PatientUnlinkView(generics.UpdateAPIView):
    """
    View for patient for unassigning a therapist.
    """

    http_method_names = ["patch"]
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = WaitingToLinkSerializer

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.request.user.assigned_to = None
        self.request.user.assignment_active = False
        self.request.user.assigned_tasks.clear()
        Meeting.objects.all().filter(assigned_patient=self.request.user).delete()
        self.request.user.save()
        return super().update(request, *args, **kwargs)
