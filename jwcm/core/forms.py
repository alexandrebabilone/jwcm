from django import forms
from jwcm.core.models import Congregation
from django.forms import Form, ModelForm


class CongregationForm(ModelForm):
    class Meta:
        model = Congregation
        fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']


class BatchPersonForm(Form):
    file = forms.FileField(label='Arquivo')
