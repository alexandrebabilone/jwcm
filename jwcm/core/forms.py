from django import forms
from jwcm.core.models import Congregation, AbstractMeeting



class CongregationForm(forms.ModelForm):
    class Meta:
        model = Congregation
        fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']


class BatchPersonForm(forms.Form):
    file = forms.FileField(label='Arquivo')


class IndicatorMicForm(forms.ModelForm):
    class Meta:
        model = AbstractMeeting
        fields = ['indicator_1', 'indicator_2', 'mic_1', 'mic_2']
