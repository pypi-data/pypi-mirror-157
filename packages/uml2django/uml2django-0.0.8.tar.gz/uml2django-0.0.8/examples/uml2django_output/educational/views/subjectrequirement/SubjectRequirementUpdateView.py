from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import SubjectRequirement
from educational.forms import SubjectRequirementUpdateForm

class SubjectRequirementUpdateView(UpdateView):
    model = SubjectRequirement
    form_class = SubjectRequirementUpdateForm
    template_name = "educational/subjectrequirement_update.html"
    success_url = reverse_lazy('subjectrequirement-list')