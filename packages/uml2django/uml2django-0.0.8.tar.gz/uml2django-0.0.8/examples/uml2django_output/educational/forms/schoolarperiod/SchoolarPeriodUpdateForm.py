from django import forms
 
from educational.models import SchoolarPeriod
 

class SchoolarPeriodUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = SchoolarPeriod
        fields = (
            'name',
            'start_date',
            'end_date',
        )