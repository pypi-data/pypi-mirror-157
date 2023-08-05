from django.views.generic import DetailView

from educational.models import SubjectClass


class SubjectClassDetailView(DetailView):
    model = SubjectClass
    template_name = "educational/subjectclass_detail.html"
