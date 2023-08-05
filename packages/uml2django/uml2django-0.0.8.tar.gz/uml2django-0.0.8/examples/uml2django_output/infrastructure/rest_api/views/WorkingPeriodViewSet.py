from rest_framework import viewsets
from rest_framework import permissions
from infrastructure.models import WorkingPeriod
from infrastructure.rest_api.serializers import WorkingPeriodSerializer


class WorkingPeriodViewSet(viewsets.ModelViewSet):
    queryset = WorkingPeriod.objects.all()
    serializer_class = WorkingPeriodSerializer
    permission_classes = [] 
