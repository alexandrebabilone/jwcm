from django.db.models import Q
from django import forms
from jwcm.core.models import Person, Congregation, PublicAssignment
from jwcm.core.widget import DatePickerInput
from jwcm.public_speeches.models import Speech



class SpeechForm(forms.ModelForm):
    class Meta:
        model = Speech
        fields = ['number', 'theme']


class PublicAssignmentForm(forms.ModelForm):
    class Meta:
        model = PublicAssignment
        fields = ['speech', 'speaker']
        #widgets = {'date': DatePickerInput(format=('%Y-%m-%d'), attrs={}),} #adicionar o campo data novamente?

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(PublicAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['speaker'].queryset = Person.objects.filter(congregation=self.request.user.profile.congregation).filter(Q(privilege=Person.ANCIAO) | Q(privilege=Person.SERVO_MINISTERIAL))


class PersonGuestForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['full_name', 'telephone', 'congregation']


class CongregationGuestPopUpForm(forms.ModelForm):
    class Meta:
        model = Congregation
        fields = ['name']
