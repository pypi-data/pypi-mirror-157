from rest_framework import viewsets
from rest_framework import permissions
from educational.models import SubjectRequirement
from educational.rest_api.serializers import SubjectRequirementSerializer


class SubjectRequirementViewSet(viewsets.ModelViewSet):
    queryset = SubjectRequirement.objects.all()
    serializer_class = SubjectRequirementSerializer
    permission_classes = [] 
