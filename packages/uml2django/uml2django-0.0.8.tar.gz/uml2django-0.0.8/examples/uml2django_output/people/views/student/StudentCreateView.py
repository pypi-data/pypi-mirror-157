
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from people.models import Student
from people.forms import StudentCreateForm

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = "people/student_create.html"
    success_url = reverse_lazy('student-list')