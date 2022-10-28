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


def choices_image_file_path(instance, filename):
    """Generate filepath for new choice image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'choices', filename)


def profile_image_file_path(instance, filename):
    """Generate filepath for new profile image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'profile', filename)


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
    assigned_tasks = models.ManyToManyField('Task', blank=True)

    image = models.ImageField(
        null=True,
        upload_to=profile_image_file_path,
        blank=True
    )
    phone = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    therapist_code = models.CharField(max_length=5, null=True, blank=True)
    bio = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        null=True,
        blank=True
    )
    assignment_active = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    @property
    def assigned_patients_count(self):
        return self.patients.count()

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Task(models.Model):
    """Model for Tasks"""
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    difficulty = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_by'
    )
    tags = models.ManyToManyField('Tag')
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    """Model for storing a question"""
    heading = models.CharField(max_length=255, blank=True)
    choices = models.ManyToManyField('BasicChoice')
    assigned_to = models.ForeignKey(
        Task,
        related_name="questions",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.heading


class CustomQuestion(models.Model):
    """Model for storing a question"""
    choices = models.ManyToManyField('CustomChoice')
    assigned_to = models.ForeignKey(
        Task,
        related_name="custom_questions",
        on_delete=models.CASCADE,
    )


class BasicChoice(models.Model):
    """Model for storing choices"""
    text = models.CharField(max_length=255)
    image = models.ImageField(null=False, upload_to=choices_image_file_path)
    assigned_to = models.ManyToManyField('Task', blank=True)
    tags = models.ManyToManyField('Tag')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text


class CustomChoice(models.Model):
    """Model for storing custom choices created by therapist"""
    text = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    assigned_to = models.ManyToManyField('Task', blank=True)
    tags = models.ManyToManyField('Tag')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text


class Tag(models.Model):
    """Model for Tags"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class TaskResult(models.Model):
    """Model for storing Task results"""
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return "Result task" + str(self.task.id)


class QuestionConnectImageAnswer(models.Model):
    """Model for storing question answers"""
    assigned_to = models.ForeignKey(
        TaskResult,
        related_name="answers",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Result question for " + str(self.assigned_to)


class Answer(models.Model):
    """Model for storing answers"""
    data1 = models.CharField(max_length=255)
    data2 = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=True)
    assigned_to_question = models.ForeignKey(
        QuestionConnectImageAnswer,
        related_name="answer",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "Result answers for " + str(self.assigned_to_question)


class Meeting(models.Model):
    """Model for storing meetings created by therapist"""
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_created_by"
    )
    assigned_patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_assigned_patient",
        blank=True,
        null=True,
    )
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.name
