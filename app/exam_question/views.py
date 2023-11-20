# Views for Exam Questions
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Exam_Question
from exam_question import serializers


class Exam_QuestionViewSet(viewsets.ModelViewSet):
    """View for managing exam_question APIs"""
    serializer_class = serializers.Exam_QuestionSerializer
    queryset = Exam_Question.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve exam questions"""
        return self.queryset.order_by('-id')
