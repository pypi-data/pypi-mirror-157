from django import forms
 
from educational.models import Subject
 

class SubjectUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Subject
        fields = (
            'title',
            'name',
        )