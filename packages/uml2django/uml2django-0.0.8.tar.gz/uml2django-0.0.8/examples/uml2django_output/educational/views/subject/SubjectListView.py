from django.views.generic import ListView

from educational.models import Subject

class SubjectListView(ListView):
    model = Subject
    template_name = "educational/subject_list.html"