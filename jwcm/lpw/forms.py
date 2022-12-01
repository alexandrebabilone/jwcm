from django import forms
from django.forms import ModelForm, Form
from jwcm.lpw.models import PersonAvailability, CongregationAvailability, DayLPW
import datetime
from jwcm.core.widget import DatePickerInput
from jwcm.core.models import Person, Congregation


class PersonAvailabilityForm(ModelForm):
    class Meta:
        model = PersonAvailability
        exclude = ['person']

    def __init__(self, *args, **kwargs):
        super(PersonAvailabilityForm, self).__init__(*args, **kwargs)
        self.fields['weekday'].disabled = True


class CongregationAvailabilityForm(ModelForm):
    class Meta:
        model = CongregationAvailability
        exclude = ['congregation']

    def __init__(self, *args, **kwargs):
        super(CongregationAvailabilityForm, self).__init__(*args, **kwargs)
        self.fields['weekday'].disabled = True


class DayLPWForm(ModelForm):
    class Meta:
        model = DayLPW
        exclude = ['congregation']

    def __init__(self, *args, **kwargs):
        self.instance = kwargs['instance']
        weekday = self.instance.weekday
        congregation = self.instance.congregation
        super(DayLPWForm, self).__init__(*args, **kwargs)
        self.fields['date'].disabled = True
        self.fields['weekday'].disabled = True
        self.fields['morning'].queryset = Person.objects.publisher_per_congregation_and_weekday_to_morning(congregation, weekday)
        self.fields['afternoon'].queryset = Person.objects.publisher_per_congregation_and_weekday_to_afternoon(congregation, weekday)
        self.fields['night'].queryset = Person.objects.publisher_per_congregation_and_weekday_to_night(congregation, weekday)



class SearchMonthlyLPWForm(Form):
    current_day = datetime.date.today()
    month_and_year = forms.DateField(initial=current_day, label='Mês/Ano', widget=DatePickerInput(format=('%Y-%m-%d'), attrs={}))
