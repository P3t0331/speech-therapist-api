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
from core.exceptions import UpdateNotAllowedException


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
        """
        Helper function for creating tags for a `BasicChoice`.
        If a tag with the given name and user does not exist in the database, it will be created.
        Then, the tag will be added to the given `BasicChoice`.
        """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            basic_choice.tags.add(tag_obj)

    def create(self, validated_data):
        """
        Create a new `BasicChoice` instance.
        The `tags` field of the `BasicChoice` will be populated with the corresponding `Tag` instances.
        """
        tags = validated_data.pop('tags', [])
        choice = BasicChoice.objects.create(**validated_data)
        self._get_or_create_tags(tags, choice)
        return choice

    def update(self, instance, validated_data):
        """
        Update a `BasicChoice` instance.
        If the `tags` field is included in the updated data, the `BasicChoice's` tags will be updated accordingly.
        """
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CustomChoiceSerializer(BasicChoiceSerializer):
    """
    Serializer for Custom Choices.
    This serializer extends the `BasicChoiceSerializer`, which means it includes the same fields and behavior.
    """
    class Meta(BasicChoiceSerializer.Meta):
        model = CustomChoice


class FourChoiceSerializer(BasicChoiceSerializer):
    """
    Serializer for Four Choice items.
    This serializer extends the `BasicChoiceSerializer`, which means it includes the same behavior for handling tags.
    """
    class Meta:
        model = FourChoice
        fields = ['id', 'question_data', 'correct_option', 'incorrect_option1', 'incorrect_option2', 'incorrect_option3']
        read_only_fields = ['id', 'created_by']

    def create(self, validated_data):
        """
        Create and return a new `FourChoice` instance, given the validated data.
        This method uses the `_get_or_create_tags()` method to populate the `tags` field of the FourChoice instance.
        """
        tags = validated_data.pop('tags', [])
        choice = FourChoice.objects.create(**validated_data)
        self._get_or_create_tags(tags, choice)
        return choice

    def update(self, instance, validated_data):
        """
        Update and return an existing FourChoice instance, given the validated data.
        This method uses the `_get_or_create_tags()` method to populate the `tags` field of the FourChoice instance.
        """
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
        """
        Populate the `choices` field of a Question instance.
        This method randomly selects 3 BasicChoice instances and adds them to the `choices` field of the given Question instance.
        """
        choices = list(BasicChoice.objects.all())
        random_choices = random.sample(choices, 3)
        for choice in random_choices:
            question.choices.add(choice)

    def create(self, validated_data):
        """
        Create and return a new Question instance, given the validated data.
        This method uses the `_get_choices()` method to populate the `choices` field of the Question instance.
        """
        question = Question.objects.create(**validated_data)
        self._get_choices(question)
        return question


class CustomQuestionSerializer(QuestionSerializer):
    """Serializer for Custom Questions"""
    choices = CustomChoiceSerializer(many=True, required=True)

    class Meta(QuestionSerializer.Meta):
        model = CustomQuestion
        fields = ['id', 'choices']

    def _get_or_create_choices(self, question, choices):
        """Get or create choices for the given question"""
        auth_user = self.context['request'].user
        for choice in choices:
            choice_obj, created = CustomChoice.objects.get_or_create(
                created_by=auth_user,
                **choice,
            )
            question.choices.add(choice_obj)

    def create(self, validated_data):
        """Create a new custom question"""
        choices = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        self._get_or_create_choices(question, choices)
        return question


class FourQuestionSerializer(serializers.ModelSerializer):
    """Serializer for Four Questions"""
    choices = FourChoiceSerializer(many=True, required=True)

    class Meta:
        model = FourQuestion
        fields = ['id', 'choices']


    def _get_or_create_choices(self, question, choices):
        """Get or create choices for the given question"""
        auth_user = self.context['request'].user
        for choice in choices:
            choice_obj, created = FourChoice.objects.get_or_create(
                created_by=auth_user,
                **choice,
            )
            question.choices.add(choice_obj)

    def create(self, validated_data):
        """Create a new four choice question"""
        question = FourQuestion.objects.create(**validated_data)
        self._get_or_create_choices(question)
        return question


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Tasks.
    Handles the serialization of tasks and their associated tags and questions.
    """
    tags = TagSerializer(many=True, required=False)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_choices(self, question, task):
        """
        Helper function to retrieve random choices for a given question and task.
        Adds the chosen choices to the question and assigns them to the task.
        """
        choices = list(BasicChoice.objects.exclude(assigned_to=task).filter(created_by=1))
        random_choices = random.sample(choices, 3)
        for choice in random_choices:
            choice.assigned_to.add(task)
            question.choices.add(choice)

    def _get_or_create_tags(self, tags, task):
        """
        Helper function to retrieve or create tags for a given task.
        Adds the retrieved/created tags to the task.
        """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            task.tags.add(tag_obj)

    def _generate_questions(self, task):
        """
        Helper function to generate questions for a given task.
        Adds the generated questions to the task.
        """
        for i in range(10):
            question = Question.objects.create(heading=f'Otazka{i}',
                                               assigned_to=task)
            self._get_choices(question, task)

    def create(self, validated_data):
        """
        Create a task.
        Generates questions and tags for the task.
        """
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        if len(list(BasicChoice.objects.exclude(assigned_to=task))) < 30:
            raise serializers.ValidationError(
                "There is not enough data to create exercise"
            )
        self._generate_questions(task)
        self._get_or_create_tags(tags, task)
        return task



class CustomTaskDetailSerializer(TaskDetailSerializer):
    """
    Serializer for custom Tasks.
    Extends the base TaskDetailSerializer to handle custom questions.
    """
    questions = CustomQuestionSerializer(many=True, required=True, source='custom_questions')

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _create_questions(self, task, questions):
        """
        Helper function to create custom questions for a given task.
        Adds the created questions to the task.
        """
        auth_user = self.context['request'].user
        for question in questions:
            choices = question.pop('choices', [])
            question_obj = CustomQuestion.objects.create(
                assigned_to=task
            )
            for choice in choices:
                tags = choice.pop('tags', [])
                choice_obj = CustomChoice.objects.create(
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
        """
        Create a custom task.
        Generates custom questions and tags for the task.
        """
        questions = validated_data.pop('custom_questions', [])
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        self._create_questions(task, questions)
        self._get_or_create_tags(tags, task)
        return task

    def update(self, instance, validated_data):
        """
        Update task.
        Updates the task's custom questions and tags if provided.
        """
        tags = validated_data.pop('tags', None)
        questions = validated_data.pop('custom_questions', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if questions is not None:
            CustomQuestion.objects.all().filter(assigned_to=instance.id).delete()
            self._create_questions(instance, questions)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class FourChoicesTaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for four choices tasks.
    Handles the serialization of four choices tasks and their associated questions and tags.
    """
    questions = FourQuestionSerializer(many=True, required=False, source='fourchoice_questions')
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags',
                  'questions']
        read_only_fields = ['id', 'created_by']

    def _get_or_create_tags(self, tags, task):
        """
        Helper function to retrieve or create tags for a given task.
        Adds the retrieved/created tags to the task.
        """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            task.tags.add(tag_obj)

    def _create_questions(self, task, questions):
        """
        Helper function to create four choice questions for a given task.
        Adds the created questions to the task.
        """
        auth_user = self.context['request'].user
        for question in questions:
            choices = question.pop('choices', [])
            question_obj = FourQuestion.objects.create(
                assigned_to=task
            )
            for choice in choices:
                tags = choice.pop('tags', [])
                choice_obj = FourChoice.objects.create(
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
        """
        Helper function to generate four choices questions with an image and text choices.
        Adds the generated choices to the provided question.
        """
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
        """
        Helper function to generate four choices questions with a text and image choices.
        Adds the generated choices to the provided question.
        """
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
        """
        Helper function to generate four choices questions for a given task.
        Generates the questions based on the provided type.
        """
        for _ in range(10):
            question = FourQuestion.objects.create(assigned_to=task)
            if type == 'Four_Choices_Image-Texts':
                self._get_choices_image_text(question, task)
            else:
                self._get_choices_text_image(question, task)

    def create(self, validated_data):
        """
        Create a four choices task.
        Generates four choices questions if no questions are provided in the validated data.
        Adds the generated/provided questions and tags to the task.
        """
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
            self._create_questions(task, questions)
        self._get_or_create_tags(tags, task)
        return task

    def update(self, instance, validated_data):
        """
        Update task.
        Updates the task's questions and tags if provided.
        """
        tags = validated_data.pop('tags', None)
        questions = validated_data.pop('fourchoice_questions', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if questions is not None:
            FourQuestion.objects.all().filter(assigned_to=instance.id).delete()
            self._create_questions(instance, questions)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class TaskSerializer(TaskDetailSerializer):
    """Serializer for Task detail view"""

    class Meta(TaskDetailSerializer.Meta):
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags']


class RandomTaskSerializer(TaskDetailSerializer):
    """Serializer for RandomTask view"""
    class Meta(TaskDetailSerializer.Meta):
        fields = ['id', 'name', 'type', 'difficulty', 'created_by', 'tags']
        read_only_fields = ['id', 'name', 'type', 'difficulty',
                            'created_by', 'tags']


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    class Meta:
        model = Answer
        fields = ['id', 'data1', 'data2', 'is_correct']
        read_only_fields = ['id']


class AnswerFourChoiceSerializer(serializers.ModelSerializer):
    """Serializer for AnswerFourChoice model"""
    class Meta:
        model = AnswerFourChoice
        fields = ['id', 'question_data', 'correct_option', 'incorrect_option1', 'incorrect_option2',
                  'incorrect_option3', 'chosen_option', 'is_correct']


class QuestionConnectImageAnswerSerializer(serializers.ModelSerializer):
    """Serializer for QuestionConnectImageAnswer model"""
    answer = AnswerSerializer(required=True, many=True)

    class Meta:
        model = QuestionConnectImageAnswer
        fields = ['id', 'answer']
        read_only_fields = ['id']

    def _create_answer(self, answers, answer):
        """Helper method to create answer objects"""
        for answer_data in answers:
            Answer.objects.create(assigned_to_question=answer, **answer_data)

    def create(self, validated_data):
        """Create and return a new QuestionConnectImageAnswer object"""
        answers = validated_data.pop('answer', [])
        answer = QuestionConnectImageAnswer.objects.create(**validated_data)
        self._create_answer(answers, answer)


class QuestionFourChoiceAnswerSerializer(QuestionConnectImageAnswerSerializer):
    """Serializer for QuestionFourChoiceAnswer model"""
    answer = AnswerFourChoiceSerializer(required=True, many=True, source='answer_fourchoice')

    def _create_answer(self, answers, answer):
        """Helper method to create answer_fourchoice objects"""
        for answer_data in answers:
            AnswerFourChoice.objects.create(assigned_to_question=answer, **answer_data)


class TaskDetailResultSerializer(serializers.ModelSerializer):
    """Serializer for task results"""
    answers = QuestionConnectImageAnswerSerializer(required=True, many=True)

    class Meta:
        model = TaskResult
        fields = ['id', 'answered_by', 'task', 'date_created', 'answers']
        read_only_fields = ['id', 'answered_by', 'date_created']

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
    """Serializer for task results with four choice answers"""
    answers = QuestionFourChoiceAnswerSerializer(required=True, many=True)

    class Meta:
        model = TaskResult
        fields = ['id', 'answered_by', 'task', 'date_created', 'answers']
        read_only_fields = ['id', 'answered_by', 'date_created']

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
    """Serializer for task results"""
    class Meta(TaskDetailResultSerializer.Meta):
        fields = ['id', 'answered_by', 'task', 'date_created']


class AssignTaskSerializer(serializers.ModelSerializer):
    """Serializer for assigning tasks to users"""
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
