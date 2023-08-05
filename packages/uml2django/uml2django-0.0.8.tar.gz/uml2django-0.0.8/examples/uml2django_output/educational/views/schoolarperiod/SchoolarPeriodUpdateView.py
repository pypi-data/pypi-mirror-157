from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from educational.models import SchoolarPeriod
from educational.forms import SchoolarPeriodUpdateForm

class SchoolarPeriodUpdateView(UpdateView):
    model = SchoolarPeriod
    form_class = SchoolarPeriodUpdateForm
    template_name = "educational/schoolarperiod_update.html"
    success_url = reverse_lazy('schoolarperiod-list')