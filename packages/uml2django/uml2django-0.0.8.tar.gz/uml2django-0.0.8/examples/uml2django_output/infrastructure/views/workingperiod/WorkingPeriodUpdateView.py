from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from infrastructure.models import WorkingPeriod
from infrastructure.forms import WorkingPeriodUpdateForm

class WorkingPeriodUpdateView(UpdateView):
    model = WorkingPeriod
    form_class = WorkingPeriodUpdateForm
    template_name = "infrastructure/workingperiod_update.html"
    success_url = reverse_lazy('workingperiod-list')