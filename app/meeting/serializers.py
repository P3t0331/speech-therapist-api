"""Serializers for meeting API"""
from rest_framework import serializers
from core.models import Meeting, User
from django.core.exceptions import ObjectDoesNotExist


class CustomSlugRelatedField(serializers.SlugRelatedField):
    """
    Custom SlugRelatedField that provides additional error handling.
    """
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            return self.fail('invalid')
        except (TypeError, ValueError):
            self.fail('invalid')


class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for meetings"""
    assigned_patient = CustomSlugRelatedField(many=False,
                                              slug_field='email',
                                              queryset=User.objects.all(),
                                              required=False)

    class Meta:
        model = Meeting
        fields = ['id', 'name', 'created_by', 'assigned_patient',
                  'start_time', 'end_time']
        read_only_fields = ['id']
