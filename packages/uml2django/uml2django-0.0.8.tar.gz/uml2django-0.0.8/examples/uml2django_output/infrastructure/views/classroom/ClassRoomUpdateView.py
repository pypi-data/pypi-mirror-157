from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from infrastructure.models import ClassRoom
from infrastructure.forms import ClassRoomUpdateForm

class ClassRoomUpdateView(UpdateView):
    model = ClassRoom
    form_class = ClassRoomUpdateForm
    template_name = "infrastructure/classroom_update.html"
    success_url = reverse_lazy('classroom-list')