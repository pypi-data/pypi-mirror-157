
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from infrastructure.models import ClassRoom
from infrastructure.forms import ClassRoomCreateForm

class ClassRoomCreateView(CreateView):
    model = ClassRoom
    form_class = ClassRoomCreateForm
    template_name = "infrastructure/classroom_create.html"
    success_url = reverse_lazy('classroom-list')