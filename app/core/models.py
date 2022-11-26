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
from django.forms.models import model_to_dict
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.timezone import timedelta


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
    day_streak = models.IntegerField(default=0)
    last_result_posted = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        null=True,
        blank=True
    )
    assignment_active = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)

    @property
    def assigned_patients_count(self):
        return self.patients.count()

    @property
    def my_meetings(self):
        res = []
        for i in Meeting.objects.filter(assigned_patient=self.id):
            res.append(model_to_dict(i))
        return res

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Task(models.Model):
    """Model for Tasks"""
    class Difficulty(models.TextChoices):
        EASY = 'Easy',
        HARD = 'Hard'

    class Type(models.TextChoices):
        four_choices_image = 'Four_Choices_Image-Texts',
        four_choices_text = 'Four_Choices_Text-Images',
        connect_pairs_text_image = 'Connect_Pairs_Text-Image',
        connect_pairs_text_text = 'Connect_Pairs_Text-Text',

    name = models.CharField(max_length=255)

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices, 
    )

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

class FourQuestion(models.Model):
    """Model for storing a question"""
    choices = models.ManyToManyField('FourChoice')
    assigned_to = models.ForeignKey(
        Task,
        related_name="fourchoice_questions",
        on_delete=models.CASCADE,
    )


class BasicChoice(models.Model):
    """Model for storing choices"""
    data1 = models.CharField(max_length=255)
    data2 = models.ImageField(null=False, upload_to=choices_image_file_path)
    assigned_to = models.ManyToManyField('Task', blank=True)
    tags = models.ManyToManyField('Tag')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.data1


class CustomChoice(models.Model):
    """Model for storing custom choices created by therapist"""
    data1 = models.CharField(max_length=255)
    data2 = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    tags = models.ManyToManyField('Tag')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.data1


class FourChoice(models.Model):
    """Model for storing 4 choices task"""
    question_data = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)
    incorrect_option1 = models.CharField(max_length=255)
    incorrect_option2 = models.CharField(max_length=255)
    incorrect_option3 = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


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
    date_created = models.DateTimeField(auto_now=False)

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


class AnswerFourChoice(models.Model):
    """Model for storing answers for four choice task"""
    question_data = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)
    incorrect_option1 = models.CharField(max_length=255)
    incorrect_option2 = models.CharField(max_length=255)
    incorrect_option3 = models.CharField(max_length=255)
    chosen_option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=True)
    assigned_to_question = models.ForeignKey(
        QuestionConnectImageAnswer,
        related_name="answer_fourchoice",
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


@receiver(pre_save, sender=TaskResult, dispatch_uid='post_save_taskresult_streak_handler')
def post_save_taskresult_streak_handler(sender, instance: TaskResult, **kargs):
    print("Result uploaded")
    user = instance.answered_by
    last_result = user.last_result_posted
    if not last_result:
        print("No Result Found")
        user.day_streak = 1
        user.save()
        return
    today = timezone.now().date()
    last_result_date = last_result.date()
    if last_result_date == today - timedelta(days=1):
        print("Found result, adding daystreak")
        user.day_streak += 1
    elif last_result_date != today:
        print("Found result, but not today or yesterday")
        user.day_streak = 1
    user.save()
