from django.views.generic import DetailView

from educational.models import SubjectRequirement


class SubjectRequirementDetailView(DetailView):
    model = SubjectRequirement
    template_name = "educational/subjectrequirement_detail.html"
