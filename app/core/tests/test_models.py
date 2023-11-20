"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValuesError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_questions(self):
        """test creating a question is successful"""
        exam_question = models.Exam_Question.objects.create(
            question="Test question?",
            choices=["A1", "A2", "A3", "A4"],
            answer="A1",
        )

        self.assertEqual(str(exam_question), exam_question.question)

    def test_create_user_answer(self):
        """Test creating user's answer to a question"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        exam_question = models.Exam_Question.objects.create(
            question="Test question?",
            choices=["A1", "A2", "A3", "A4"],
            answer="A1",
        )
        user_answer = models.User_Answer.objects.create(
            user=user,
            question=exam_question,
            user_answer="Test Answer",
            iscorrect=False,
            issubmitted=True,
            isbookmarked=True,
        )

        self.assertEqual(str(user_answer), user_answer.user_answer)
