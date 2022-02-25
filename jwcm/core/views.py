from django.views.generic import TemplateView, UpdateView
from django.http import HttpResponseRedirect
from jwcm.core.forms import CongregationChoiceForm, UserForm, CongregationForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Profile


class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'


def user_register(request):
    user_form = UserForm(request.POST or None)
    congregation_choice_form = CongregationChoiceForm(request.POST or None)
    congregation_form = CongregationForm(request.POST or None)
    print('antes do if')

    if request.method == 'POST':
        print('dentro do if POST')
        congregation_choice = int(request.POST.get('congregation_choice'))

        if (not congregation_choice_form.is_valid()) or (not user_form.is_valid()):
            print('nao valido')
            return render(request, 'core/register.html',
                          {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})

        if congregation_choice == congregation_choice_form.CONGREGACAO_EXISTENTE:
            congregation_key = congregation_choice_form.cleaned_data['congregation_key']

            qs = Congregation.objects.filter(random_key=congregation_key)
            if qs.exists():
                print(f'Existe congregação com este código {congregation_key}')
                congregation = qs.get()
                user = user_form.save()
                profile = Profile.objects.create(congregation=congregation, user=user)
                messages.success(request, 'Usuário cadastrado com sucesso.')
                return HttpResponseRedirect(r('login'))
            else:
                print(f'Não existe congregação com este código {congregation_key}')
                messages.error(request, 'Não existe congregação com este código.')
                return render(request, 'core/register.html',
                              {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})

        else: #criar nova congregação
            if congregation_form.is_valid():
                new_congregation = congregation_form.save()
                user = user_form.save()
                profile = Profile.objects.create(congregation=new_congregation, user=user)
                messages.success(request, 'Usuário e Congregação cadastrados com sucesso.')
                return HttpResponseRedirect(r('login'))
            else:
                return render(request, 'core/register.html',
                              {'congregation_choice_form': congregation_choice_form, 'user_form': user_form,
                               'congregation_form': congregation_form})

    else:
        print('AQUI NAO ERA P VIR')
        return render(request, 'core/register.html', {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})


class ProfileUpdateView(UpdateView):
    template_name = 'core/update_profile.html'
    model = Profile
    fields = ['telephone']
    success_url = reverse_lazy('home')

class CongregationUpdateView(UpdateView):
    template_name = 'core/update_congregation.html'
    model = Congregation
    fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day', 'random_key']
    success_url = reverse_lazy('home')

