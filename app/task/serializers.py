"""
Serializers for Task APIs
"""
import random

from rest_framework import serializers
from core.models import Task, Question, BasicChoice


class BasicChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Basic Choices"""
    class Meta:
        model = BasicChoice
        fields = ['id', 'text', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Questions"""
    choices = BasicChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'heading', 'choices']
        read_only_fields = ['id']

    def _get_choices(self, question):
        choices = list(BasicChoice.objects.all())
        random_choices = random.sample(choices, 3)
        for choice in random_choices:
            question.choices.add(choice)

    def create(self, validated_data):
        question = Question.objects.create(**validated_data)
        self._get_choices(question)
        return question


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Tasks"""
    questions = QuestionSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by',
                  'questions']
        read_only_fields = ['id', 'created_by', 'questions']

    def _get_choices(self, question, task):
        choices = list(BasicChoice.objects.exclude(assigned_to=task))
        if len(choices) < 30:
            raise serializers.ValidationError(
                "There is not enough data to create exercise with "
                f"this type, upload more images! (Missing: {30-len(choices)})"
                )
        random_choices = random.sample(choices, 3)
        for choice in random_choices:
            choice.assigned_to.add(task)
            question.choices.add(choice)

    def _create_questions(self, task):
        for i in range(10):
            question = Question.objects.create(heading=f'Otazka{i}')
            self._get_choices(question, task)
            task.questions.add(question)

    def create(self, validated_data):
        """Create a task"""
        task = Task.objects.create(**validated_data)
        self._create_questions(task)
        return task

    def update(self, instance, validated_data):
        """Update task"""
        questions = validated_data.pop('questions', None)
        if questions is not None:
            instance.questions.clear()
            self._create_questions(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
