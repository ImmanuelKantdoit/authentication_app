"""
Test for question APIs
"""
import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Exam_Question

from exam_question.serializers import Exam_QuestionSerializer


EXAM_QUESTION_URL = reverse('exam_question:exam_question-list')


def create_question(**params):
    """Create and return a sample question"""
    defaults = {
        'question': 'sample question?',
        'choices': ['A', 'B', 'C', 'D'],
        'answer': 'C'
    }
    defaults.update(params)

    exam_question = Exam_Question.objects.create(**defaults)
    return exam_question


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(EXAM_QUESTION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_questions(self):
        """Test retrieving a list of recipes"""
        create_question()
        create_question()

        res = self.client.get(EXAM_QUESTION_URL)

        exam_questions = Exam_Question.objects.all().order_by('-id')
        serializer = Exam_QuestionSerializer(exam_questions, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_exam_question_detail(self):
        """Test get recipe detail"""
        exam_question = create_question()

        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"
        res = self.client.get(url)

        serializer = Exam_QuestionSerializer(exam_question)
        self.assertEqual(res.data, serializer.data)

    def test_create_exam_question(self):
        """Test creating questions"""
        payload = {
            'question': 'sample question?',
            'choices': '["Test1", "Test2", "Test3", "Test4"]',
            'answer': 'Test3',
        }
        res = self.client.post(EXAM_QUESTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exam = Exam_Question.objects.get(id=res.data['id'])

        # manual conversion of JSON to list for payload
        payload_choices = json.loads(payload['choices'])

        for k, v in payload.items():
            if k == 'choices':
                self.assertEqual(
                    payload_choices,
                    json.loads(getattr(exam, k))
                    if isinstance(getattr(exam, k), str)
                    else getattr(exam, k)
                )
            else:
                self.assertEqual(getattr(exam, k), v)

    def test_partial_update_question(self):
        """Test partial update of an exam question"""
        original_answer = "C"
        exam_question = create_question(
            question='Sample question?',
            choices=["A", "B", "C"],
            answer=original_answer,
        )
        payload = {'question': 'New question'}
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the instance from the database
        exam_question.refresh_from_db()

        # Ensure that the question is updated
        self.assertEqual(exam_question.question, payload['question'])

        # Ensure that the answer is unchanged
        self.assertEqual(exam_question.answer, original_answer)

    def test_partial_update_choices_answer(self):
        """Test partial update of an exam question"""
        original_question = "Sample question"
        exam_question = create_question(
            question=original_question,
            choices='["Test1", "Test2", "Test3", "Test4"]',
            answer="Test4",
        )
        payload = {
            'choices': '["Choice1", "Choice2", "Choice3","Choice4"]',
            'answer': "Choice1",
        }
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the instance from the database
        exam_question.refresh_from_db()

        # Ensure that the choices is updated
        self.assertEqual(json.loads(payload['choices']), exam_question.choices)

        # Ensure that the answer is updated
        self.assertEqual(payload['answer'], exam_question.answer)

        # Ensure that the question is unchanged
        self.assertEqual(original_question, exam_question.question)

    def test_partial_update_choices_only(self):
        """Test partial update of an exam question"""
        original_question = "Sample question"
        original_answer = "Test3"
        exam_question = create_question(
            question=original_question,
            choices=["Test1", "Test2", "Test3", "Test4"],
            answer=original_answer,
        )
        payload = {'choices': '["Choice1", "Choice2", "Choice3","Choice4"]'}
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Refresh the instance from the database
        exam_question.refresh_from_db()

        # Ensure that the choices is changed
        self.assertEqual(exam_question.choices, json.loads(payload['choices']))

        # Ensure answer is changes based on the index of the old answer
        self.assertNotEqual(exam_question.answer, original_answer)
        self.assertEqual(exam_question.answer, "Choice3")

        # Ensure that the question is unchanged
        self.assertEqual(exam_question.question, original_question)

    def test_partial_update_withdifflength_choices_only(self):
        """Test partial update of an exam question"""
        original_question = "Sample question"
        original_answer = "Test3"
        exam_question = create_question(
            question=original_question,
            choices=["Test1", "Test2", "Test3", "Test4"],
            answer=original_answer,
        )
        payload = {'choices': '["Choice1", "Choice2"]'}
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Refresh the instance from the database
        exam_question.refresh_from_db()

        # Ensure that the choices is changed
        self.assertEqual(exam_question.choices, json.loads(payload['choices']))

        # Ensure answer is changes based on the index of the old answer
        self.assertNotEqual(exam_question.answer, original_answer)
        self.assertEqual(exam_question.answer, None)

        # Ensure that the question is unchanged
        self.assertEqual(exam_question.question, original_question)

    def test_partial_update_answer_only_answer_is_in_choices(self):
        """Test partial update of an exam question"""
        original_question = "Sample question"
        original_choices = '["Test1", "Test2", "Test3", "Test4"]'
        exam_question = create_question(
            question=original_question,
            choices=original_choices,
            answer="Test4",
        )
        payload = {'answer': "Test3"}
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Refresh the instance from the database
        exam_question.refresh_from_db()

        # Ensure that the answer is changed
        self.assertEqual(exam_question.answer, payload['answer'])

        # Ensure that the choices is unchanged
        self.assertEqual(exam_question.choices, original_choices)

        # Ensure that the question is unchanged
        self.assertEqual(exam_question.question, original_question)

    def test_partial_update_answer_only_answer_is_not_in_choices(self):
        """Test partial update of an exam question"""
        original_question = "Sample question"
        original_choices = '["Choice1", "Choice2", "Choice3"]'
        exam_question = create_question(
            question=original_question,
            choices=original_choices,
            answer="Choice3",
        )
        payload = {'answer': "D"}
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"

        # Use a context manager to catch the expected ValueError
        with self.assertRaises(ValueError) as context:
            self.client.patch(url, payload)
        # Assert that the exception was raised
        self.assertEqual(
            str(context.exception),
            "Answer must be in the current choices"
            )

    def test_full_update(self):
        """Test full update of an exam question"""
        exam_question = create_question(
            question="Sample question",
            choices='["Test1", "Test2", "Test3", "Test4"]',
            answer="Test4",
        )
        payload = {
            'question': "Updated question",
            'choices': '["Choice1", "Choice2", "Choice3", "Choice4"]',
            'answer': "Choice4",
        }
        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        exam_question.refresh_from_db()
        for k, v in payload.items():
            if k == 'choices':
                expected_choices = json.loads(payload['choices'])
                actual_choices = (
                    json.loads(getattr(exam_question, k))
                    if isinstance(getattr(exam_question, k), str)
                    else getattr(exam_question, k)
                )
                self.assertEqual(expected_choices, actual_choices)
            else:
                self.assertEqual(getattr(exam_question, k), v)

    def test_delete_exam_question(self):
        """Test deleting an exam_question successful"""
        exam_question = create_question()

        url = reverse('exam_question:exam_question-list')
        + f"{exam_question.id}/"
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Exam_Question.objects.filter(
                id=exam_question.id).exists()
            )

    def test_answer_in_choices(self):
        """Test that answer is contained in choices"""
        payload = {
            'question': "Question",
            'choices': '["Choice1", "Choice2", "Choice3", "Choice4"]',
            'answer': "Choice4",
        }
        res = self.client.post(EXAM_QUESTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exam = Exam_Question.objects.get(id=res.data['id'])

        # Ensure answer is in choices
        self.assertIn(exam.answer, exam.choices)
        self.assertIn(payload['answer'], payload['choices'])
