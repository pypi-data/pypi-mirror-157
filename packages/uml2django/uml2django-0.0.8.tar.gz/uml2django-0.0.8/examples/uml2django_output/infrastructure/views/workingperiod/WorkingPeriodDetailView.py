from django.views.generic import DetailView

from infrastructure.models import WorkingPeriod


class WorkingPeriodDetailView(DetailView):
    model = WorkingPeriod
    template_name = "infrastructure/workingperiod_detail.html"
