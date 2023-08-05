
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import Subject
from educational.forms import SubjectCreateForm

class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectCreateForm
    template_name = "educational/subject_create.html"
    success_url = reverse_lazy('subject-list')