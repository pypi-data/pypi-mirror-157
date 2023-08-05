from django import forms
 
from educational.models import SubjectClass
 

class SubjectClassUpdateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = SubjectClass
        fields = (
            'subject',
            'subject_level',
            'title',
            'capacity',
            'start_date',
            'end_date',
        )