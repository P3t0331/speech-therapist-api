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
    """Serializer for Tasks"""
    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty']
        read_only_fields = ['id', 'created_by']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    assigned_tasks = TaskSerializerForUser(many=True, required=False)
    assigned_to = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='email'
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
                  'image', 'is_therapist', 'assigned_tasks',
                  'assigned_to', 'assigment_active']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'style': {'input_type': 'password'}
                }
            }
        read_only_fields = ['id', 'is_therapist',
                            'assigned_tasks', 'assigned_to',
                            'assigment_active']

    def validate(self, data):
        """
        Checks to be sure that the received password and confirm_password
        fields are exactly the same
        """
        if data.get('password') != data.pop('confirm_password', None):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class PatientViewSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['notes']


class UserTherapistSerializer(UserSerializer):
    """Serializer for the therapist user object"""
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'name', 'password', 'confirm_password',
                  'is_therapist', 'image',
                  'phone', 'location', 'country', 'company',
                  'therapist_code']
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
        letters = ascii_lowercase
        result_str = ''.join(choice(letters) for i in range(length))
        return result_str

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        validated_data['therapist_code'] = self._generate_code()
        return get_user_model().objects.create_therapist_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and auth the user"""
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
    """Serializer for assigning therapists"""
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
        ).update(assigned_to=therapist)
        instance.assigned_to = therapist
        return instance


class WaitingToLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'image',
                  'assigned_to', 'assigment_active']
        read_only_fields = ['id', 'email', 'name',
                            'image', 'assigned_to',
                            'assigment_active']


class UpdateNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['notes']

    def update(self, instance, validated_data):
        my_view = self.context['view']
        object_id = my_view.kwargs.get('pk')
        get_user_model().objects.all().filter(
            id=object_id
        ).update(notes=validated_data.get('notes'))
        instance.notes = validated_data.get('notes')
        return super().update(instance, validated_data)
