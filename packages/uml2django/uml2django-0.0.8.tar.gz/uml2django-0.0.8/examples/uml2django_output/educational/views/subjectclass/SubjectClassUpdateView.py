from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import SubjectClass
from educational.forms import SubjectClassUpdateForm

class SubjectClassUpdateView(UpdateView):
    model = SubjectClass
    form_class = SubjectClassUpdateForm
    template_name = "educational/subjectclass_update.html"
    success_url = reverse_lazy('subjectclass-list')