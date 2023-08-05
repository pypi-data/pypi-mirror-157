from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import Subject

class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = "educational/subject_delete.html"
    success_url = reverse_lazy('subject-list')
