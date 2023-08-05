from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from educational.models import SchoolarPeriod

class SchoolarPeriodDeleteView(DeleteView):
    model = SchoolarPeriod
    template_name = "educational/schoolarperiod_delete.html"
    success_url = reverse_lazy('schoolarperiod-list')
