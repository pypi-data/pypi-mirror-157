from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from people.models import Instructor

class InstructorDeleteView(DeleteView):
    model = Instructor
    template_name = "people/instructor_delete.html"
    success_url = reverse_lazy('instructor-list')
