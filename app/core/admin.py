"""
Django admin cust
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'name', 'is_therapist']
    list_filter = ('is_active', 'is_superuser', 'is_therapist')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'assigned_tasks')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_therapist',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
                'is_therapist',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Task)
admin.site.register(models.Question)
admin.site.register(models.BasicChoice)
admin.site.register(models.Tag)
admin.site.register(models.TaskResult)
admin.site.register(models.QuestionConnectImageAnswer)
admin.site.register(models.Answer)
