from django.views.generic import ListView

from educational.models import SubjectRequirement

class SubjectRequirementListView(ListView):
    model = SubjectRequirement
    template_name = "educational/subjectrequirement_list.html"