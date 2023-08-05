from rest_framework import viewsets
from rest_framework import permissions
from educational.models import SubjectClassSchedulePeriod
from educational.rest_api.serializers import SubjectClassSchedulePeriodSerializer


class SubjectClassSchedulePeriodViewSet(viewsets.ModelViewSet):
    queryset = SubjectClassSchedulePeriod.objects.all()
    serializer_class = SubjectClassSchedulePeriodSerializer
    permission_classes = [] 
