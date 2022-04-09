from django import forms
from jwcm.core.models import Congregation, Person



class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['full_name', 'telephone', 'gender', 'privilege', 'modality']


class CongregationForm(forms.ModelForm):
    class Meta:
        model = Congregation
        fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']


class BatchPersonForm(forms.Form):
    file = forms.FileField(label='Arquivo')
