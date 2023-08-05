from django.views.generic import ListView

from educational.models import SubjectClassSchedulePeriod

class SubjectClassSchedulePeriodListView(ListView):
    model = SubjectClassSchedulePeriod
    template_name = "educational/subjectclassscheduleperiod_list.html"