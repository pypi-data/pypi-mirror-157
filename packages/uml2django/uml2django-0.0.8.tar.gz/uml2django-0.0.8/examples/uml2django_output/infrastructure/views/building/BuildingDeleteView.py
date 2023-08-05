from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from infrastructure.models import Building

class BuildingDeleteView(DeleteView):
    model = Building
    template_name = "infrastructure/building_delete.html"
    success_url = reverse_lazy('building-list')
