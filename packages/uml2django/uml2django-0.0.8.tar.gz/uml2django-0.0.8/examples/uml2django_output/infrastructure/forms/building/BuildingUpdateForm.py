from django import forms
 
from infrastructure.models import Building
 

class BuildingUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Building
        fields = (
            'name',
        )