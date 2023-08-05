from django.views.generic import DetailView

from infrastructure.models import Building


class BuildingDetailView(DetailView):
    model = Building
    template_name = "infrastructure/building_detail.html"
