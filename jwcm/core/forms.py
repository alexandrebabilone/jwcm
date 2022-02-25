from django import forms
from django.core.exceptions import ValidationError
from jwcm.core.models import Speech, Congregation, Person, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['full_name', 'telephone', 'gender', 'privilege', 'modality']


class SpeechForm(forms.ModelForm):
    class Meta:
        model = Speech
        fields = ['number', 'theme']


class CongregationForm(forms.ModelForm):
    class Meta:
        model = Congregation
        fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']


class UserForm(UserCreationForm):
    email = forms.EmailField(max_length=100) #quando eu declaro o campo aqui (sendo que ele já existe), ele se torna obrigatório

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        #help_texts = {'username': 'Nome de Usuário'}

    def clean_email(self):
        e = self.cleaned_data['email']

        if User.objects.filter(email=e).exists():
            raise ValidationError("O email {} já está em uso.".format(e))

        return e


class CongregationChoiceForm(forms.Form):
    CONGREGACAO_EXISTENTE = 0
    CONGREGACAO_NOVA = 1

    CHOICES = (
        (CONGREGACAO_EXISTENTE, 'Vincular minha conta a uma congregação existente'),
        (CONGREGACAO_NOVA, 'Cadastrar nova congregação')
    )

    congregation_choice = forms.ChoiceField(label='Defina sua Congregação', widget=forms.RadioSelect(attrs={'onclick':'change_congregation_choice()'}), choices=CHOICES, initial=CONGREGACAO_EXISTENTE)
    congregation_key = forms.CharField(max_length=50, label='Código da Congregação', required=False)
