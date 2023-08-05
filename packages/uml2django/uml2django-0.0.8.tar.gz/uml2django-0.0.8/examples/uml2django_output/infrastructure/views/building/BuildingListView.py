from django.views.generic import ListView

from infrastructure.models import Building

class BuildingListView(ListView):
    model = Building
    template_name = "infrastructure/building_list.html"