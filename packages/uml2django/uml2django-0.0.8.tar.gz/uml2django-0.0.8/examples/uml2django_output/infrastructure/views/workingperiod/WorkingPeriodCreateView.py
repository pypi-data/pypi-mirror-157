
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from infrastructure.models import WorkingPeriod
from infrastructure.forms import WorkingPeriodCreateForm

class WorkingPeriodCreateView(CreateView):
    model = WorkingPeriod
    form_class = WorkingPeriodCreateForm
    template_name = "infrastructure/workingperiod_create.html"
    success_url = reverse_lazy('workingperiod-list')