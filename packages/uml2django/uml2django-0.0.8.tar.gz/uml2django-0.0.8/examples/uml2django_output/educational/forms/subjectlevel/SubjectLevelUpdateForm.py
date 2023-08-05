from django import forms
 
from educational.models import SubjectLevel
 

class SubjectLevelUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = SubjectLevel
        fields = (
            'subject',
            'title',
            'description',
        )