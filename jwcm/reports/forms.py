from django import forms
from django.core.exceptions import ValidationError
from jwcm.core.widget import DatePickerInput
import datetime
from django.forms import Form



class ReportsForm(Form):
    current_day = datetime.date.today()
    start_date = forms.DateField(initial=current_day, label='Início', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))
    end_date = forms.DateField(initial=current_day + datetime.timedelta(weeks=1), label='Fim', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))


    def clean(self):
        _start = self.cleaned_data.get('start_date')
        _end = self.cleaned_data.get('end_date')

        if _start >= _end:
            raise ValidationError('A data final deve ser maior que a data inicial.')

        return self.cleaned_data
