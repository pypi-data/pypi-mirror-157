from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import SubjectClassSchedulePeriod

class SubjectClassSchedulePeriodDeleteView(DeleteView):
    model = SubjectClassSchedulePeriod
    template_name = "educational/subjectclassscheduleperiod_delete.html"
    success_url = reverse_lazy('subjectclassscheduleperiod-list')
