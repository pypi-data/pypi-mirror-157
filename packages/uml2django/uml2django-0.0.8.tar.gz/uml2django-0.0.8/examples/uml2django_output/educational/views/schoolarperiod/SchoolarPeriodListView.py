from django.views.generic import ListView

from educational.models import SchoolarPeriod

class SchoolarPeriodListView(ListView):
    model = SchoolarPeriod
    template_name = "educational/schoolarperiod_list.html"