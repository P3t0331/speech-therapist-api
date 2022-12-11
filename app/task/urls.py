"""Url mapping for Task API"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from task import views

router = DefaultRouter()
router.register("tasks", views.TaskViewSet)
router.register("basic_choices", views.BasicChoiceViewSet)
router.register("tags", views.TagViewSet)
router.register("results", views.TaskResultViewSet)

app_name = "task"

urlpatterns = [path("", include(router.urls))]
