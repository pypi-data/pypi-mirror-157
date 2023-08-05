
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import SubjectRequirement
from educational.forms import SubjectRequirementCreateForm

class SubjectRequirementCreateView(CreateView):
    model = SubjectRequirement
    form_class = SubjectRequirementCreateForm
    template_name = "educational/subjectrequirement_create.html"
    success_url = reverse_lazy('subjectrequirement-list')