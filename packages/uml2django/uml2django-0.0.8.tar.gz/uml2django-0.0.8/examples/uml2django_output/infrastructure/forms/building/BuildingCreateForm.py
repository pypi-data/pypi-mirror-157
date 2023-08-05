from django import forms

from infrastructure.models import Building
 

class BuildingCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Building
        fields = (
            'name',
        )
