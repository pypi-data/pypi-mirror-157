from django.views.generic import ListView

from infrastructure.models import WorkingPeriod

class WorkingPeriodListView(ListView):
    model = WorkingPeriod
    template_name = "infrastructure/workingperiod_list.html"