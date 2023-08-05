from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import SubjectClassSchedulePeriod
from educational.forms import SubjectClassSchedulePeriodUpdateForm

class SubjectClassSchedulePeriodUpdateView(UpdateView):
    model = SubjectClassSchedulePeriod
    form_class = SubjectClassSchedulePeriodUpdateForm
    template_name = "educational/subjectclassscheduleperiod_update.html"
    success_url = reverse_lazy('subjectclassscheduleperiod-list')