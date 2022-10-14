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
    path('list/', views.ListUserView.as_view(), name='list-users'),
    path('list/<pk>', views.GetUser.as_view(), name='get-user'),
]
