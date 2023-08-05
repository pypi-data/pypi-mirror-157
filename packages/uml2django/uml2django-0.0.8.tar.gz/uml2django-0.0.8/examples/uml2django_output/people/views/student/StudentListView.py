from django.views.generic import ListView

from people.models import Student

class StudentListView(ListView):
    model = Student
    template_name = "people/student_list.html"