"""Url mapping for Meeting API"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from meeting import views

router = DefaultRouter()
router.register("meetings", views.MeetingViewSet)

app_name = "meeting"

urlpatterns = [path("", include(router.urls))]
