from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from people.models import Student
from people.forms import StudentUpdateForm

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = "people/student_update.html"
    success_url = reverse_lazy('student-list')