from django.views.generic import ListView

from people.models import Instructor

class InstructorListView(ListView):
    model = Instructor
    template_name = "people/instructor_list.html"