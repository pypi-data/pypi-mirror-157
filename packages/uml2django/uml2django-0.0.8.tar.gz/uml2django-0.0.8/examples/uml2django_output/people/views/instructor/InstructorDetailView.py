from django.views.generic import DetailView

from people.models import Instructor


class InstructorDetailView(DetailView):
    model = Instructor
    template_name = "people/instructor_detail.html"
