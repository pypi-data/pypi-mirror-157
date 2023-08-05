from django.views.generic import DetailView

from educational.models import SubjectLevel


class SubjectLevelDetailView(DetailView):
    model = SubjectLevel
    template_name = "educational/subjectlevel_detail.html"
