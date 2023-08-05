from django.views.generic import DetailView

from educational.models import SchoolarPeriod


class SchoolarPeriodDetailView(DetailView):
    model = SchoolarPeriod
    template_name = "educational/schoolarperiod_detail.html"
