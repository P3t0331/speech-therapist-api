"""
URL Mappings for the user API
"""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('patient/register/', views.CreatePatientView.as_view(),
         name='create-patient'),
    path('therapist/register/', views.CreateTherapistView.as_view(),
         name='create-therapist'),
    path('login/', views.CreateTokenView.as_view(), name='token'),
    path('patient/myprofile/', views.ManagerUserView.as_view(),
         name='me-patient'),
    path('therapist/myprofile/', views.ManagerUserTherapistView.as_view(),
         name='me-therapist'),
    path('list/patients/',
         views.ListPatientUserView.as_view(), name='list-patients'),
    path('list/therapists/',
         views.ListTherapistUserView.as_view(), name='list-therapists'),
    path('list/patient/<pk>/',
         views.GetPatientUserView.as_view(), name='get-patient-user'),
    path('list/therapist/<pk>/',
         views.GetTherapistUserView.as_view(), name='get-therapist-user'),
    path('patient/link/',
         views.AssignTherapistView.as_view(), name='assign-therapist'),
    path('therapist/waiting-to-link/',
         views.PatientsWaitingToLinkView.as_view(), name='waiting-for-link'),
    path('therapist/link/<pk>/accept/',
         views.AcceptLinkView.as_view(), name='accept-link'),
    path('therapist/link/<pk>/reject/',
         views.RejectLinkView.as_view(), name='reject-link'),
    path('therapist/<pk>/note/',
         views.UpdateNoteView.as_view(), name='update-note'),
    path('therapist/link/<pk>/unlink/',
         views.TherapistUnlinkView.as_view(), name='therapist-unlink-patient'),
    path('patient/unlink/',
         views.PatientUnlinkView.as_view(), name='unlink-patient'),
]
