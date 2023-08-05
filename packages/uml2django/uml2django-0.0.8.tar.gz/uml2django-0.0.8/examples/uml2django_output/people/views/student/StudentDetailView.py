from django.views.generic import DetailView

from people.models import Student


class StudentDetailView(DetailView):
    model = Student
    template_name = "people/student_detail.html"
