
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from educational.models import SchoolarPeriod
from educational.forms import SchoolarPeriodCreateForm

class SchoolarPeriodCreateView(CreateView):
    model = SchoolarPeriod
    form_class = SchoolarPeriodCreateForm
    template_name = "educational/schoolarperiod_create.html"
    success_url = reverse_lazy('schoolarperiod-list')