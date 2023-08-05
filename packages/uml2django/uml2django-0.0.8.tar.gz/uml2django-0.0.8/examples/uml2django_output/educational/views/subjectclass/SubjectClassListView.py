from django.views.generic import ListView

from educational.models import SubjectClass

class SubjectClassListView(ListView):
    model = SubjectClass
    template_name = "educational/subjectclass_list.html"