from django import forms
from django.core.exceptions import ValidationError
from jwcm.core.models import Congregation, Meeting
from jwcm.core.widget import DatePickerInput
import datetime
from django.forms import Form, ModelForm, BaseModelFormSet


class CongregationForm(ModelForm):
    class Meta:
        model = Congregation
        fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']


class BatchPersonForm(Form):
    file = forms.FileField(label='Arquivo')


class MechanicalPrivileges(Form):
    current_day = datetime.date.today()
    start_date = forms.DateField(initial=current_day, label='Início', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))
    end_date = forms.DateField(initial=current_day + datetime.timedelta(weeks=10), label='Fim', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))

    def clean(self):
        _start = self.cleaned_data.get('start_date')
        _end = self.cleaned_data.get('end_date')

        if _start >= _end:
            raise ValidationError('A data final deve ser maior que a data inicial.')

        return self.cleaned_data


class MeetingMechanicalPrivilegesForm(ModelForm):

    class Meta:
        model = Meeting
        fields = ['date', 'indicator_1', 'indicator_2', 'mic_1', 'mic_2', 'note_sound_table', 'zoom_indicator']


class BulletinForm(Form):
    current_day = datetime.date.today()
    start_date = forms.DateField(initial=current_day, label='Início', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))
    end_date = forms.DateField(initial=current_day + datetime.timedelta(weeks=1), label='Fim', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))


    def clean(self):
        _start = self.cleaned_data.get('start_date')
        _end = self.cleaned_data.get('end_date')

        if _start >= _end:
            raise ValidationError('A data final deve ser maior que a data inicial.')

        return self.cleaned_data
