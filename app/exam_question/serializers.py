from rest_framework import serializers
from core.models import Exam_Question


class Exam_QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.JSONField()

    class Meta:
        model = Exam_Question
        fields = ['id', 'question', 'choices', 'answer']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # 'choices' is now a Python object, no need for manual conversion
        return representation

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        # 'choices' is automatically converted from JSON to Python
        return internal_value

    def validate(self, data):

        # 'choices' is automatically converted from JSON to Python
        return data

    def create(self, validated_data):
        choices = validated_data.get('choices', [])
        answer = validated_data.get('answer')

        if answer is not None and answer not in choices:
            raise ValueError("Answer must be in the choices")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Ensure that partial updates are allowed
        # partial = getattr(self, 'partial', False)

        if (
             'choices' in validated_data
             and 'answer' in validated_data
        ):
            # Update both choices and answer together
            self.update_choices_and_answer(instance, validated_data)
            exit
        else:
            if (
                'choices' in validated_data
                and 'answer' not in validated_data
            ):
                # Update choices only
                self.update_choices(instance, validated_data)
            elif (
                'answer' in validated_data
                and 'choices' not in validated_data
            ):
                # Update answer only
                self.update_answer(instance, validated_data)

        # Adjusted to use instance.choices directly
        instance.choices = validated_data.get('choices', instance.choices)

        instance = super().update(instance, validated_data)
        return instance

    def update_choices(self, instance, validated_data):
        new_choices = validated_data.get('choices', [])
        old_choices = instance.choices
        answer = instance.answer

        if (
            answer is not None
            and answer in old_choices
            and answer not in new_choices
        ):
            answer_pos = old_choices.index(answer)
            if answer_pos < len(new_choices):
                validated_data['answer'] = new_choices[answer_pos]
            else:
                validated_data['answer'] = None
        else:
            validated_data['answer'] = answer

    def update_answer(self, instance, validated_data):
        current_answer = validated_data.get('answer')
        current_choices = instance.choices

        if current_answer is not None and current_answer in current_choices:
            validated_data['answer'] = current_answer
        else:
            raise ValueError("Answer must be in the current choices")

    def update_choices_and_answer(self, instance, validated_data):
        new_choices = validated_data.get('choices', [])
        old_choices = instance.choices
        answer = validated_data['answer']

        if (
            answer is not None
            and answer in old_choices
            and answer not in new_choices
        ):
            raise ValueError("New answer must be in the new choices")

        elif (
            answer is not None
            and answer in old_choices
            and answer in new_choices
        ):
            validated_data['answer'] = answer

        elif (
            answer is not None
            and answer not in old_choices
            and answer in new_choices
        ):
            validated_data['answer'] = answer

        else:
            raise ValueError("New answer must be in the new choices")
