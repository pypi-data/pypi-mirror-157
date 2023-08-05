from django import forms

from infrastructure.models import ClassRoom
 

class ClassRoomCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = ClassRoom
        fields = (
            'building',
            'name',
        )
