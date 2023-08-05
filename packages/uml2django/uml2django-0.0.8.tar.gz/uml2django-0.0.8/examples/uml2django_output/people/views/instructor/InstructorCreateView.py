
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from people.models import Instructor
from people.forms import InstructorCreateForm

class InstructorCreateView(CreateView):
    model = Instructor
    form_class = InstructorCreateForm
    template_name = "people/instructor_create.html"
    success_url = reverse_lazy('instructor-list')