from rest_framework import viewsets
from rest_framework import permissions
from educational.models import SubjectLevel
from educational.rest_api.serializers import SubjectLevelSerializer


class SubjectLevelViewSet(viewsets.ModelViewSet):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer
    permission_classes = [] 
