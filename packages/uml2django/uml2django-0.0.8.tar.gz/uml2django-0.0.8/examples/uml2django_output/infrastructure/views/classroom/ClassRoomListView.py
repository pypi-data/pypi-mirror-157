from django.views.generic import ListView

from infrastructure.models import ClassRoom

class ClassRoomListView(ListView):
    model = ClassRoom
    template_name = "infrastructure/classroom_list.html"