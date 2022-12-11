"""
Django admin cust
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""

    ordering = ["id"]
    list_display = ["email", "name", "is_therapist"]
    list_filter = ("is_active", "is_superuser", "is_therapist")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "name",
                    "assigned_tasks",
                    "image",
                    "phone",
                    "location",
                    "country",
                    "company",
                    "therapist_code",
                    "assigned_to",
                    "day_streak",
                    "last_result_posted",
                    "notes",
                    "diagnosis",
                    "bio",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_therapist",
                    "assignment_active",
                )
            },
        ),
        (_("Important data"), {"fields": ("last_login",)}),
    )
    readonly_fields = ["last_login"]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_therapist",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Task)
admin.site.register(models.Question)
admin.site.register(models.BasicChoice)
admin.site.register(models.Tag)
admin.site.register(models.TaskResult)
admin.site.register(models.QuestionConnectImageAnswer)
admin.site.register(models.Answer)
admin.site.register(models.AnswerFourChoice)
admin.site.register(models.Meeting)

admin.site.register(models.CustomChoice)
admin.site.register(models.CustomQuestion)

admin.site.register(models.FourChoice)
admin.site.register(models.FourQuestion)
