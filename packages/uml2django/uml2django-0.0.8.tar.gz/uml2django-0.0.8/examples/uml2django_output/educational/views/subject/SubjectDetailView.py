from django.views.generic import DetailView

from educational.models import Subject


class SubjectDetailView(DetailView):
    model = Subject
    template_name = "educational/subject_detail.html"
