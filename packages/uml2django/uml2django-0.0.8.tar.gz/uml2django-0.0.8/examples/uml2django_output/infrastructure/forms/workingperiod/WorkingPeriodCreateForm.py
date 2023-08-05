from django import forms

from infrastructure.models import WorkingPeriod
 

class WorkingPeriodCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = WorkingPeriod
        fields = (
            'building',
            'class_room',
            'day_of_week',
            'from_hour',
            'to_time',
        )
