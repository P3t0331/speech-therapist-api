"""
Serializers for Task APIs
"""

from rest_framework import serializers

from core.models import Task, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choices"""

    class Meta:
        model = Choice
        fields = ['data', 'left_side', 'assigned_to_identifier']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Questions"""
    left_choice = ChoiceSerializer(many=True, required=False)
    right_choice = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['heading', 'left_choice', 'right_choice']

    def _get_or_create_choices(self, choices, question):
        for choice in choices:
            choice_obj, created = Choice.objects.get_or_create(
                **choice
            )
            if choice.side is True:
                question.left_choice.add(choice_obj)
            else:
                question.right_choice.add(choice_obj)

    def create(self, validated_data):
        left_choices = validated_data.pop('left_choice', [])
        right_choices = validated_data.pop('right_choice', [])

        question = Question.objects.create(**validated_data)
        self._get_or_create_choices(left_choices, question)
        self._get_or_create_choices(right_choices, question)
        return question


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Tasks"""
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_or_create_questions(self, questions, task):
        for question in questions:
            question_obj, created = Question.objects.get_or_create(
                **question
            )
            task.questions.add(question_obj)

    def create(self, validated_data):
        """Create a task"""
        questions = validated_data.pop('questions', [])
        task = Task.objects.create(**validated_data)
        self._get_or_create_questions(questions, task)
        return task

    def update(self, instance, validated_data):
        """Update task"""
        questions = validated_data.pop('questions', None)
        if questions is not None:
            instance.questions.clear()
            self._get_or_create_questions(questions, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
