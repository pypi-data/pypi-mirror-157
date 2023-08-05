
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import SubjectClassSchedulePeriod
from educational.forms import SubjectClassSchedulePeriodCreateForm

class SubjectClassSchedulePeriodCreateView(CreateView):
    model = SubjectClassSchedulePeriod
    form_class = SubjectClassSchedulePeriodCreateForm
    template_name = "educational/subjectclassscheduleperiod_create.html"
    success_url = reverse_lazy('subjectclassscheduleperiod-list')