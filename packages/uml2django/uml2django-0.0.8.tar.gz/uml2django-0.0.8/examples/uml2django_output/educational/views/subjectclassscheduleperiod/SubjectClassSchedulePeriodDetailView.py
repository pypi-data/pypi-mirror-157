from django.views.generic import DetailView

from educational.models import SubjectClassSchedulePeriod


class SubjectClassSchedulePeriodDetailView(DetailView):
    model = SubjectClassSchedulePeriod
    template_name = "educational/subjectclassscheduleperiod_detail.html"
