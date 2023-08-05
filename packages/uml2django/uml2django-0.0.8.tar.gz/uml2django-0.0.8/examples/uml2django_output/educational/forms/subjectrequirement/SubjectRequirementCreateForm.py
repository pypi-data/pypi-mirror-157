from django import forms

from educational.models import SubjectRequirement
 

class SubjectRequirementCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = SubjectRequirement
        fields = (
            'subject',
            'title',
            'description',
        )
