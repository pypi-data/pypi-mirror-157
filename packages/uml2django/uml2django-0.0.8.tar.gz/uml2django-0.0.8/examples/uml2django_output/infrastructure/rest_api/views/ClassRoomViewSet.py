from rest_framework import viewsets
from rest_framework import permissions
from infrastructure.models import ClassRoom
from infrastructure.rest_api.serializers import ClassRoomSerializer


class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [] 
    lookup_field = 'slug'
