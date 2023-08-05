from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from infrastructure.models import ClassRoom

class ClassRoomDeleteView(DeleteView):
    model = ClassRoom
    template_name = "infrastructure/classroom_delete.html"
    success_url = reverse_lazy('classroom-list')
