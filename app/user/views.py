"""
Views for the user api
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, UserTherapistSerializer
from user.serializers import AuthTokenSerializer
from core.models import User

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


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'therapist_only',
                OpenApiTypes.INT, enum=[0, 1],
                description="Filter users to list only therapists"
            ),
            OpenApiParameter(
                'patient_only',
                OpenApiTypes.INT, enum=[0, 1],
                description="Filter users to list only patients"
            )
        ]
    )
)
class ListUserView(generics.ListAPIView):
    """List users"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        therapist_only = bool(
            int(self.request.query_params.get('therapist_only', 0))
        )
        patient_only = bool(
            int(self.request.query_params.get('patient_only', 0))
        )
        queryset = User.objects.all()
        if therapist_only:
            queryset = queryset.filter(is_therapist=True)
        elif patient_only:
            queryset = queryset.filter(is_therapist=False)
        return queryset

class GetUser(generics.RetrieveAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
