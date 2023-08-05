from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import Subject
from educational.forms import SubjectUpdateForm

class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectUpdateForm
    template_name = "educational/subject_update.html"
    success_url = reverse_lazy('subject-list')