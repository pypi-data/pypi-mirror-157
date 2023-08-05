from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import SubjectRequirement

class SubjectRequirementDeleteView(DeleteView):
    model = SubjectRequirement
    template_name = "educational/subjectrequirement_delete.html"
    success_url = reverse_lazy('subjectrequirement-list')
