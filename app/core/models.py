"""
Database models
"""
import uuid
import os


from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


def recipe_image_file_path(instance, filename):
    """Generate filepath for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_therapist = True
        user.save(using=self._db)

        return user

    def create_therapist_user(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_therapist = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_therapist = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Question(models.Model):
    heading = models.CharField(max_length=255, blank=True)
    choices = models.ManyToManyField('BasicChoice')

    def __str__(self):
        return self.heading


class Task(models.Model):
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    difficulty = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField('Tag')
    questions = models.ManyToManyField('Question')

    def __str__(self):
        return self.name


class BasicChoice(models.Model):
    text = models.CharField(max_length=255)
    image = models.ImageField(null=False, upload_to=recipe_image_file_path)
    assigned_to = models.ManyToManyField('Task', blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.text


class Tag(models.Model):
    text = models.CharField(max_length=255)
