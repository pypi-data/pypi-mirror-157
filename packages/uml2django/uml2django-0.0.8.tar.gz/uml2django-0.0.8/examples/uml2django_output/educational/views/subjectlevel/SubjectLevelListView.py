from django.views.generic import ListView

from educational.models import SubjectLevel

class SubjectLevelListView(ListView):
    model = SubjectLevel
    template_name = "educational/subjectlevel_list.html"