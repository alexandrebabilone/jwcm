from django.core.management.utils import get_random_secret_key
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from jwcm.lpw.models import CongregationAvailability
from jwcm.users.forms import UserForm, CongregationChoiceForm
from django.views.generic import UpdateView
from jwcm.users.models import Profile
from jwcm.core.forms import CongregationForm
from jwcm.core.models import Congregation
from django.shortcuts import render, resolve_url as r



def user_register(request):
    user_form = UserForm(request.POST or None)
    congregation_choice_form = CongregationChoiceForm(request.POST or None)
    congregation_form = CongregationForm(request.POST or None)
    template_name = 'register.html'

    if request.method == 'POST':
        congregation_choice = int(request.POST.get('congregation_choice'))

        if (not congregation_choice_form.is_valid()) or (not user_form.is_valid()):
            return render(request, template_name,
                          {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})

        if congregation_choice == congregation_choice_form.CONGREGACAO_EXISTENTE:
            congregation_key = congregation_choice_form.cleaned_data['congregation_key']

            qs = Congregation.objects.filter(random_key=congregation_key)
            if qs.exists():
                congregation = qs.get()
                user = user_form.save()
                profile = Profile.objects.create(congregation=congregation, user=user)
                messages.success(request, 'Usuário cadastrado com sucesso.')
                return HttpResponseRedirect(r('login'))
            else:
                messages.error(request, 'Não existe congregação com este código.')
                return render(request, template_name,
                              {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})

        else: #criar nova congregação
            if congregation_form.is_valid():
                congregation_form.instance.random_key = get_random_secret_key()
                congregation_form.instance.host = True
                new_congregation = congregation_form.save()
                user = user_form.save()
                profile = Profile.objects.create(congregation=new_congregation, user=user)

                for weekday in range(0, 7):
                    congregation_availability = CongregationAvailability.objects.create(weekday=weekday)
                    congregation_availability.congregation.add(new_congregation)

                messages.success(request, 'Usuário e Congregação cadastrados com sucesso.')
                return HttpResponseRedirect(r('login'))
            else:
                return render(request, template_name,
                              {'congregation_choice_form': congregation_choice_form, 'user_form': user_form,
                               'congregation_form': congregation_form})

    else:
        return render(request, template_name, {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})


class ProfileUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'form.html'
    model = Profile
    fields = ['telephone']
    success_url = reverse_lazy('home')
    success_message = "Perfil alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Perfil'
        context['button'] = 'Salvar'
        return context
