
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import SubjectLevel
from educational.forms import SubjectLevelCreateForm

class SubjectLevelCreateView(CreateView):
    model = SubjectLevel
    form_class = SubjectLevelCreateForm
    template_name = "educational/subjectlevel_create.html"
    success_url = reverse_lazy('subjectlevel-list')