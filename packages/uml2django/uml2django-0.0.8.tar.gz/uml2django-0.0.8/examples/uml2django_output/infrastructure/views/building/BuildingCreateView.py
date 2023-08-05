
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from infrastructure.models import Building
from infrastructure.forms import BuildingCreateForm

class BuildingCreateView(CreateView):
    model = Building
    form_class = BuildingCreateForm
    template_name = "infrastructure/building_create.html"
    success_url = reverse_lazy('building-list')