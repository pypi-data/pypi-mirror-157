from rest_framework import viewsets
from rest_framework import permissions
from infrastructure.models import Building
from infrastructure.rest_api.serializers import BuildingSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [] 
    lookup_field = 'slug'
