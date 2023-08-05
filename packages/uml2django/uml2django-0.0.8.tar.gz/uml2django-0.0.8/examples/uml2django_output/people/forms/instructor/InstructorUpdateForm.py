from django import forms
 
from people.models import Instructor
 

class InstructorUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Instructor
        fields = (
            'ufrrj_id',
        )