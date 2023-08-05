from django import forms
 
from people.models import Student
 

class StudentUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Student
        fields = (
            'ufrrj_id',
        )