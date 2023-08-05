from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from infrastructure.models import WorkingPeriod

class WorkingPeriodDeleteView(DeleteView):
    model = WorkingPeriod
    template_name = "infrastructure/workingperiod_delete.html"
    success_url = reverse_lazy('workingperiod-list')
