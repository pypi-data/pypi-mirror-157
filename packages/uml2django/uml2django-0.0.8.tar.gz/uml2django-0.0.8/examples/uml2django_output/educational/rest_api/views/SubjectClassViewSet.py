from rest_framework import viewsets
from rest_framework import permissions
from educational.models import SubjectClass
from educational.rest_api.serializers import SubjectClassSerializer


class SubjectClassViewSet(viewsets.ModelViewSet):
    queryset = SubjectClass.objects.all()
    serializer_class = SubjectClassSerializer
    permission_classes = [] 
