from rest_framework import viewsets
from rest_framework import permissions
from educational.models import Subject
from educational.rest_api.serializers import SubjectSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [] 
    lookup_field = 'slug'
