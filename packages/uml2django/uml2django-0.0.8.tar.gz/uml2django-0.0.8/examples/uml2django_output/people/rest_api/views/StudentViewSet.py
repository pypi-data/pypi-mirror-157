from rest_framework import viewsets
from rest_framework import permissions
from people.models import Student
from people.rest_api.serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [] 
