from rest_framework import viewsets
from rest_framework import permissions
from educational.models import SchoolarPeriod
from educational.rest_api.serializers import SchoolarPeriodSerializer


class SchoolarPeriodViewSet(viewsets.ModelViewSet):
    queryset = SchoolarPeriod.objects.all()
    serializer_class = SchoolarPeriodSerializer
    permission_classes = [] 
