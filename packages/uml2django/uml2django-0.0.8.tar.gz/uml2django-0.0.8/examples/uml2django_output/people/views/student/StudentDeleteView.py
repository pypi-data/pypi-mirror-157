from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from people.models import Student

class StudentDeleteView(DeleteView):
    model = Student
    template_name = "people/student_delete.html"
    success_url = reverse_lazy('student-list')
