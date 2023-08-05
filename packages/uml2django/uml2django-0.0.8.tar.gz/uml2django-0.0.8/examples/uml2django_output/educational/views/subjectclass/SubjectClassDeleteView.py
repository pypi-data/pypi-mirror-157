from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import SubjectClass

class SubjectClassDeleteView(DeleteView):
    model = SubjectClass
    template_name = "educational/subjectclass_delete.html"
    success_url = reverse_lazy('subjectclass-list')
