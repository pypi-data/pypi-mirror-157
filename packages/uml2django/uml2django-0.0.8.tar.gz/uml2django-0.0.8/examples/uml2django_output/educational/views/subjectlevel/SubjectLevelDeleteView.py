from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import SubjectLevel

class SubjectLevelDeleteView(DeleteView):
    model = SubjectLevel
    template_name = "educational/subjectlevel_delete.html"
    success_url = reverse_lazy('subjectlevel-list')
