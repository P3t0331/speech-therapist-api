"""
Serializers for Task APIs
"""
import random

from rest_framework import serializers
from core.models import (
    Task,
    Question,
    BasicChoice,
    Tag,
    TaskResult,
    Answer,
    QuestionConnectImageAnswer,
    User,
    CustomChoice,
    CustomQuestion,
    FourChoice,
    FourQuestion,
    AnswerFourChoice,
)
from user.serializers import UserSerializer


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
        fields = ['id', 'data1', 'data2', 'tags', 'created_by']
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


class CustomChoiceSerializer(BasicChoiceSerializer):

    class Meta(BasicChoiceSerializer.Meta):
        model = CustomChoice


class FourChoiceSerializer(BasicChoiceSerializer):

    class Meta:
        model = FourChoice
        fields = ['id', 'question_data', 'correct_option', 'incorrect_option1', 'incorrect_option2', 'incorrect_option3']
        read_only_fields = ['id', 'created_by']

    def _get_or_create_tags(self, tags, four_choice):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            four_choice.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        choice = FourChoice.objects.create(**validated_data)
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


class CustomQuestionSerializer(QuestionSerializer):

    choices = CustomChoiceSerializer(many=True, required=True)

    class Meta(QuestionSerializer.Meta):
        model = CustomQuestion
        fields = ['id', 'choices']
    def _get_or_create_choices(self, question, choices):
        auth_user = self.context['request'].user
        for choice in choices:
            choice_obj, created = CustomChoice.objects.get_or_create(
                created_by=auth_user,
                **choice,
            )
            question.choices.add(choice_obj)

    def create(self, validated_data):
        choices = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        self._get_or_create_choices(question, choices)
        return question


class FourQuestionSerializer(serializers.ModelSerializer):

    choices = FourChoiceSerializer(many=True, required=True)

    class Meta:
        model = FourQuestion
        fields = ['id', 'choices']


    def _get_or_create_choices(self, question, choices):
        auth_user = self.context['request'].user
        for choice in choices:
            choice_obj, created = FourChoice.objects.get_or_create(
                created_by=auth_user,
                **choice,
            )
            question.choices.add(choice_obj)

    def create(self, validated_data):
        question = FourQuestion.objects.create(**validated_data)
        self._get_or_create_choices(question)
        return question


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer for Tasks"""
    tags = TagSerializer(many=True, required=False)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_choices(self, question, task):
        choices = list(BasicChoice.objects.exclude(assigned_to=task).filter(created_by=1))
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
            question = Question.objects.create(heading=f'Otazka{i}',
                                               assigned_to=task)
            self._get_choices(question, task)

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
            self._generate_questions(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CustomTaskDetailSerializer(TaskDetailSerializer):
    questions = CustomQuestionSerializer(many=True, required=True, source='custom_questions')

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_or_create_questions(self, task, questions):
        auth_user = self.context['request'].user
        for question in questions:
            choices = question.pop('choices', [])
            question_obj, created = CustomQuestion.objects.get_or_create(
                assigned_to=task
            )
            for choice in choices:
                tags = choice.pop('tags', [])
                choice_obj, created = CustomChoice.objects.get_or_create(
                    created_by=auth_user,
                    assigned_to=task,
                    **choice,
                )
                for tag in tags:
                    tag_obj, created = Tag.objects.get_or_create(
                        user=auth_user,
                        **tag,
                    )
                    choice_obj.tags.add(tag_obj)
                question_obj.choices.add(choice_obj)

    def create(self, validated_data):
        """Create a custom task"""
        questions = validated_data.pop('custom_questions', [])
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        self._get_or_create_questions(task, questions)
        self._get_or_create_tags(tags, task)
        return task

    def update(self, instance, validated_data):
        """Update task"""
        tags = validated_data.pop('tags', None)
        questions = validated_data.pop('custom_questions', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if questions is not None:
            instance.questions.clear()
            self._get_or_create_questions(instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class FourChoicesTaskDetailSerializer(serializers.ModelSerializer):
    questions = FourQuestionSerializer(many=True, required=False, source='fourchoice_questions')
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_or_create_tags(self, tags, task):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            task.tags.add(tag_obj)

    def _get_or_create_questions(self, task, questions):
        auth_user = self.context['request'].user
        for question in questions:
            choices = question.pop('choices', [])
            question_obj, created = FourQuestion.objects.get_or_create(
                assigned_to=task
            )
            for choice in choices:
                tags = choice.pop('tags', [])
                choice_obj, created = FourChoice.objects.get_or_create(
                    **choice,
                )
                for tag in tags:
                    tag_obj, created = Tag.objects.get_or_create(
                        user=auth_user,
                        **tag,
                    )
                    choice_obj.tags.add(tag_obj)
                question_obj.choices.add(choice_obj)

    def _get_choices_image_text(self, question, task):
        choices = list(BasicChoice.objects.exclude(assigned_to=task).filter(created_by=1))
        random_choices = random.sample(choices, 4)
        first_choice = random_choices.pop()
        request = self.context.get('request')
        choice = FourChoice.objects.create(
            question_data = request.build_absolute_uri(first_choice.data2.url),
            correct_option = first_choice.data1,
            incorrect_option1 = random_choices.pop().data1,
            incorrect_option2 = random_choices.pop().data1,
            incorrect_option3 = random_choices.pop().data1,
            assigned_to=task
        )
        question.choices.add(choice)

    def _get_choices_text_image(self, question, task):
        choices = list(BasicChoice.objects.exclude(assigned_to=task).filter(created_by=1))
        random_choices = random.sample(choices, 4)
        first_choice = random_choices.pop()
        request = self.context.get('request')
        choice = FourChoice.objects.create(
            question_data = first_choice.data1,
            correct_option = request.build_absolute_uri(first_choice.data2.url),
            incorrect_option1 = request.build_absolute_uri(random_choices.pop().data2.url),
            incorrect_option2 = request.build_absolute_uri(random_choices.pop().data2.url),
            incorrect_option3 = request.build_absolute_uri(random_choices.pop().data2.url),
            assigned_to=task
        )
        question.choices.add(choice)


    def _generate_questions(self, task, type):
        for _ in range(10):
            question = FourQuestion.objects.create(assigned_to=task)
            if type == 'Four_Choices_Image-Texts':
                self._get_choices_image_text(question, task)
            else:
                self._get_choices_text_image(question, task)

    def create(self, validated_data):
        questions = validated_data.pop('fourchoice_questions', [])
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        if questions == []:
            if len(list(BasicChoice.objects.exclude(assigned_to=task))) < 40:
                raise serializers.ValidationError(
                    "There is not enough data to create exercise"
                )
            self._generate_questions(task, task.type)
        else:
            self._get_or_create_questions(task, questions)
        self._get_or_create_tags(tags, task)
        return task


class TaskSerializer(TaskDetailSerializer):
    """Serializer for Task detail view"""

    class Meta(TaskDetailSerializer.Meta):
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags']


class RandomTaskSerializer(TaskDetailSerializer):
    class Meta(TaskDetailSerializer.Meta):
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags']
        read_only_fields = ['id', 'name', 'type', 'difficulty',
                            'created_by', 'tags']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'data1', 'data2', 'is_correct']
        read_only_fields = ['id']


class AnswerFourChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerFourChoice
        fields = ['id', 'question_data', 'correct_option', 'incorrect_option1', 'incorrect_option2',
                  'incorrect_option3', 'chosen_option', 'is_correct']


class QuestionConnectImageAnswerSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(required=True, many=True)

    class Meta:
        model = QuestionConnectImageAnswer
        fields = ['id', 'answer']
        read_only_fields = ['id']

    def _create_answer(self, answers, answer):
        for answer_data in answers:
            Answer.objects.create(assigned_to_question=answer, **answer_data)

    def create(self, validated_data):
        answers = validated_data.pop('answer', [])
        answer = QuestionConnectImageAnswer.objects.create(**validated_data)
        self._create_answer(answers, answer)


class QuestionFourChoiceAnswerSerializer(QuestionConnectImageAnswerSerializer):
    answer = AnswerFourChoiceSerializer(required=True, many=True, source='answer_fourchoice')

    def _create_answer(self, answers, answer):
        for answer_data in answers:
            AnswerFourChoice.objects.create(assigned_to_question=answer, **answer_data)


class TaskDetailResultSerializer(serializers.ModelSerializer):
    """Serializer for task results"""
    answers = QuestionConnectImageAnswerSerializer(required=True, many=True)

    class Meta:
        model = TaskResult
        fields = ['id', 'answered_by', 'task', 'answers']
        read_only_fields = ['id', 'answered_by']

    def create(self, validated_data):
        """Create a result"""
        if (TaskResult.objects.filter(
                answered_by=self.context['request'].user,
                task=validated_data.get('task')
            ) is not None
        ):
            TaskResult.objects.filter(
                answered_by=self.context['request'].user,
                task=validated_data.get('task')
            ).delete()

        answers = validated_data.pop('answers', [])
        result = TaskResult.objects.create(**validated_data)

        for answers_data in answers:
            answer = answers_data.pop('answer', [])
            question = QuestionConnectImageAnswer.objects.create(
                assigned_to=result,
                **answers_data
            )
            for answer_data in answer:
                Answer.objects.create(assigned_to_question=question,
                                      **answer_data)
        return result


class TaskDetailFourChoiceResultSerializer(serializers.ModelSerializer):
    answers = QuestionFourChoiceAnswerSerializer(required=True, many=True)

    class Meta:
        model = TaskResult
        fields = ['id', 'answered_by', 'task', 'answers']
        read_only_fields = ['id', 'answered_by']

    def create(self, validated_data):
        """Create a result"""
        if (TaskResult.objects.filter(
                answered_by=self.context['request'].user,
                task=validated_data.get('task')
            ) is not None
        ):
            TaskResult.objects.filter(
                answered_by=self.context['request'].user,
                task=validated_data.get('task')
            ).delete()

        answers = validated_data.pop('answers', [])
        result = TaskResult.objects.create(**validated_data)

        for answers_data in answers:
            answer = answers_data.pop('answer_fourchoice', [])
            question = QuestionConnectImageAnswer.objects.create(
                assigned_to=result,
                **answers_data
            )
            for answer_data in answer:
                AnswerFourChoice.objects.create(assigned_to_question=question,
                                      **answer_data)
        return result


class TaskResultSerializer(TaskDetailResultSerializer):
    class Meta(TaskDetailResultSerializer.Meta):
        fields = ['id', 'answered_by', 'task']


class AssignTaskSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(many=True, slug_field='email',
                                         queryset=User.objects.all(),
                                         write_only=True)
    user_set = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['user_set', 'users']

    def update(self, instance, validated_data):
        users = validated_data.pop('users', None)
        instance = super().update(instance, validated_data)

        if users:
            for user in users:
                instance.user_set.add(user)
            instance.save()
        return instance
