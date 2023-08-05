
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import SubjectClass
from educational.forms import SubjectClassCreateForm

class SubjectClassCreateView(CreateView):
    model = SubjectClass
    form_class = SubjectClassCreateForm
    template_name = "educational/subjectclass_create.html"
    success_url = reverse_lazy('subjectclass-list')