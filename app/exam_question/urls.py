"""
URL mappings for the exam_questions app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from exam_question import views


router = DefaultRouter()
router.register('exam_question', views.Exam_QuestionViewSet)

app_name = 'exam_question'

urlpatterns = [
    path('', include(router.urls)),
]
