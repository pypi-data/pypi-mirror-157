from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from people.models import Instructor
from people.forms import InstructorUpdateForm

class InstructorUpdateView(UpdateView):
    model = Instructor
    form_class = InstructorUpdateForm
    template_name = "people/instructor_update.html"
    success_url = reverse_lazy('instructor-list')