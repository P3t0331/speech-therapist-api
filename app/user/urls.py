"""
URL Mappings for the user API
"""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('register/patient/', views.CreatePatientView.as_view(),
         name='create-patient'),
    path('register/therapist/', views.CreateTherapistView.as_view(),
         name='create-therapist'),
    path('login/', views.CreateTokenView.as_view(), name='token'),
    path('myprofile/', views.ManagerUserView.as_view(), name='me'),
]
