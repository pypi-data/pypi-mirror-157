from rest_framework import viewsets
from rest_framework import permissions
from people.models import Instructor
from people.rest_api.serializers import InstructorSerializer


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [] 
