"""
Serializers for Task APIs
"""
from queue import Empty
import random

from rest_framework import serializers
from core.models import Task, Question, BasicChoice, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'user']
        read_only_fields = ['id', 'user']


class BasicChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Basic Choices"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = BasicChoice
        fields = ['id', 'text', 'image', 'tags', 'created_by']
        read_only_fields = ['id', 'created_by']
        extra_kwargs = {'image': {'required': 'True'}}

    def _get_or_create_tags(self, tags, basic_choice):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            basic_choice.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        choice = BasicChoice.objects.create(**validated_data)
        self._get_or_create_tags(tags, choice)
        return choice

    def update(self, instance, validated_data):
        """Update recipe"""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer for Tasks"""
    tags = TagSerializer(many=True, required=False)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id']

    def _get_choices(self, question, task):
        choices = list(BasicChoice.objects.exclude(assigned_to=task))
        random_choices = random.sample(choices, 3)
        for choice in random_choices:
            choice.assigned_to.add(task)
            question.choices.add(choice)

    def _get_or_create_tags(self, tags, task):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            task.tags.add(tag_obj)

    def _generate_questions(self, task):
        for i in range(10):
            question = Question.objects.create(heading=f'Otazka{i}')
            self._get_choices(question, task)
            task.questions.add(question)

    def create(self, validated_data):
        """Create a task"""
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        if len(list(BasicChoice.objects.exclude(assigned_to=task))) < 30:
            raise serializers.ValidationError(
                "There is not enough data to create exercise"
            )
        self._generate_questions(task)
        self._get_or_create_tags(tags, task)
        return task

    def update(self, instance, validated_data):
        """Update task"""
        tags = validated_data.pop('tags', None)
        questions = validated_data.pop('questions', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if questions is not None:
            instance.questions.clear()
            self._create_questions(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class TaskSerializer(TaskDetailSerializer):
    """Serializer for Task detail view"""

    class Meta(TaskDetailSerializer.Meta):
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags']
