from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from infrastructure.models import Building
from infrastructure.forms import BuildingUpdateForm

class BuildingUpdateView(UpdateView):
    model = Building
    form_class = BuildingUpdateForm
    template_name = "infrastructure/building_update.html"
    success_url = reverse_lazy('building-list')