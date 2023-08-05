from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import SubjectLevel
from educational.forms import SubjectLevelUpdateForm

class SubjectLevelUpdateView(UpdateView):
    model = SubjectLevel
    form_class = SubjectLevelUpdateForm
    template_name = "educational/subjectlevel_update.html"
    success_url = reverse_lazy('subjectlevel-list')