"""
Serializers for the user API view
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
    )
from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Task
from core.exceptions import CodeDoesntExistException

from string import ascii_lowercase
from random import choice


class TaskSerializerForUser(serializers.ModelSerializer):
    """
    Serializer for representing tasks assigned to users.
    """
    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty']
        read_only_fields = ['id', 'created_by']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for representing users.
    """
    assigned_tasks = TaskSerializerForUser(many=True, required=False)
    assigned_to = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )
    confirm_password = serializers.CharField(
        allow_blank=False,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'password', 'confirm_password',
                  'image', 'is_therapist', 'day_streak', 'my_meetings', 'assigned_tasks',
                  'assigned_to', 'assignment_active']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'style': {'input_type': 'password'}
                }
            }
        read_only_fields = ['id', 'is_therapist',
                            'assigned_tasks', 'assigned_to',
                            'assignment_active', 'day_streak']

    def validate(self, data):
        """
        Validate that the password and confirm_password fields are the same.
        """
        if data.get('password') != data.pop('confirm_password', None):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """
        Create and return a user with encrypted password.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return user.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class PatientViewSerializer(UserSerializer):
    """
    Serializer for representing patients and their notes and diagnoses.
    """
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['notes', 'diagnosis']


class UserTherapistSerializer(UserSerializer):
    """
    Serializer for creating and representing therapist users.
    """
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'name', 'password', 'confirm_password',
                  'is_therapist', 'image',
                  'phone', 'location', 'country', 'company', 'bio',
                  'therapist_code', 'assigned_patients_count']
        extra_kwargs = {
            'therapist_code': {
                'read_only': True
                },
            'password': {
                'write_only': True,
                'min_length': 8,
                'style': {'input_type': 'password'}
                }
            }

    def _generate_code(self, length=5):
        """
        Generate a random alphabetic code for the therapist.
        """
        letters = ascii_lowercase
        result_str = ''.join(choice(letters) for i in range(length))
        return result_str

    def create(self, validated_data):
        """
        Create and return a therapist user with encrypted password and a random therapist code.
        """
        validated_data['therapist_code'] = self._generate_code()
        return get_user_model().objects.create_therapist_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating users with their email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """
        Validate the provided email and password and return the authenticated user.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class AssignTherapistSerializer(serializers.ModelSerializer):
    """
    Serializer for assigning patients to therapists based on therapist codes.
    """
    assigned_to = serializers.SlugRelatedField(
        many=False,
        slug_field='email',
        read_only=True
    )

    class Meta:
        model = get_user_model()
        fields = ['therapist_code', 'assigned_to']
        extra_kwargs = {
            'therapist_code': {'write_only': True},
        }

    def update(self, instance, validated_data):
        """
        Assign the current user (patient) to the therapist with the specified code.
        """
        code = validated_data.pop('therapist_code')
        try:
            therapist = get_user_model().objects.get(therapist_code=code)
        except:
            raise CodeDoesntExistException(
                detail={"therapist_code": "This code doesnt exist"}
            )
        user_id = self.context['request'].user.id
        get_user_model().objects.filter(
            id=user_id
        ).update(assigned_to=therapist, assignment_active=False)
        instance.assigned_to = therapist
        instance.assignment_active = False
        return instance


class WaitingToLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a user who is waiting to be linked to an therapist.
    """
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'image', 'assigned_tasks',
                  'assigned_to', 'assignment_active']
        read_only_fields = ['id', 'email', 'name',
                            'image', 'assigned_tasks', 'assigned_to',
                            'assignment_active']


class UpdateUserFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for updating fields on a user model.
    """
    class Meta:
        model = get_user_model()
        fields = []  # this will be overridden in child classes

    def update(self, instance, validated_data):
        """
        Update the specified fields on the user instance.
        """
        my_view = self.context['view']
        object_id = my_view.kwargs.get('pk')
        get_user_model().objects.all().filter(
            id=object_id
        ).update(**validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        return super().update(instance, validated_data)


class UpdateNoteSerializer(UpdateUserFieldSerializer):
    """
    Serializer for updating the 'notes' field on a user model.
    """
    class Meta(UpdateUserFieldSerializer.Meta):
        fields = ['notes']


class UpdateDiagnosisSerializer(UpdateUserFieldSerializer):
    """
    Serializer for updating the 'diagnosis' field on a user model.
    """
    class Meta(UpdateUserFieldSerializer.Meta):
        fields = ['diagnosis']