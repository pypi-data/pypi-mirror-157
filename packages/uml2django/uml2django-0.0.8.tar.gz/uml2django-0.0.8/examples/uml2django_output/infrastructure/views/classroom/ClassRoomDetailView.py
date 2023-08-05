from django.views.generic import DetailView

from infrastructure.models import ClassRoom


class ClassRoomDetailView(DetailView):
    model = ClassRoom
    template_name = "infrastructure/classroom_detail.html"
