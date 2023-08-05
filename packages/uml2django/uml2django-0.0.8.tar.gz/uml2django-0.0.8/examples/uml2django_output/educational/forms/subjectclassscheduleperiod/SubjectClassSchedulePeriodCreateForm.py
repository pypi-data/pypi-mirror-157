from django import forms

from educational.models import SubjectClassSchedulePeriod
 

class SubjectClassSchedulePeriodCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = SubjectClassSchedulePeriod
        fields = (
            'subject_class',
            'day_of_week',
            'from_hour',
            'to_time',
        )
