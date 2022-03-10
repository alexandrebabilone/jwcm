from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from django.db.models.deletion import ProtectedError
from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponseRedirect
from jwcm.core.forms import CongregationChoiceForm, UserForm, CongregationForm, PublicAssignmentForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Profile, Person, Speech, PublicAssignment


class Home(TemplateView):
    template_name = 'home.html'


class About(TemplateView):
    template_name = 'about.html'


#******************** SUPERUSER FUNCTIONS ********************#

#******************** CREATE ********************#
def user_register(request):
    user_form = UserForm(request.POST or None)
    congregation_choice_form = CongregationChoiceForm(request.POST or None)
    congregation_form = CongregationForm(request.POST or None)
    template_name = 'core/register.html'

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
                new_congregation = congregation_form.save()
                user = user_form.save()
                profile = Profile.objects.create(congregation=new_congregation, user=user)
                messages.success(request, 'Usuário e Congregação cadastrados com sucesso.')
                return HttpResponseRedirect(r('login'))
            else:
                return render(request, template_name,
                              {'congregation_choice_form': congregation_choice_form, 'user_form': user_form,
                               'congregation_form': congregation_form})

    else:
        return render(request, template_name, {'congregation_choice_form': congregation_choice_form, 'user_form': user_form, 'congregation_form': congregation_form})


def public_assignment_create(request):
    template_name = 'core/form.html'
    public_assignment_form = PublicAssignmentForm(request.POST or None, request=request)

    if request.method == 'POST':
        if not public_assignment_form.is_valid():
            context_data = {'form': public_assignment_form,
                            'title': 'Designação',
                            'button': 'Cadastrar'}

            return render(request, template_name, context_data)

        public_assignment_form.instance.congregation = request.user.profile.congregation
        public_assignment_form.save()
        messages.success(request, f"Designação do dia {public_assignment_form.cleaned_data['date']} criada com sucesso.")
        return HttpResponseRedirect(r('public-assignment-list'))
    else:
        context_data = {'form': public_assignment_form,
                        'title': 'Designação',
                        'button': 'Cadastrar'}

        return render(request, template_name, context_data)


class PersonCreate(CreateView):
    model = Person
    template_name = 'core/form.html'
    fields = ['full_name', 'telephone', 'gender', 'privilege', 'modality', 'reader', 'indicator_mic', 'student_parts']
    success_url = reverse_lazy('person-list')
    success_message = "%(full_name)s foi registrado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Registrar Publicador'
        context['button'] = 'Salvar'
        return context

    def form_valid(self, form):
        # antes do "super" o objeto não foi criado nem salvo no banco
        form.instance.congregation = self.request.user.profile.congregation
        return super().form_valid(form)


class SpeechCreate(CreateView):
    model = Speech
    template_name = 'core/form.html'
    fields = ['number', 'theme']
    success_url = reverse_lazy('speech-list')
    success_message = "O discurso número %(number)s foi registrado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Registrar Discurso'
        context['button'] = 'Salvar'
        return context


#******************** UPDATE ********************#
def public_assignment_update(request, pk):
    template_name = 'core/form.html'
    instance = get_object_or_404(PublicAssignment, pk=pk)

    if request.method == 'POST':
        public_assignment_form = PublicAssignmentForm(request.POST, instance=instance, request=request)

        if not public_assignment_form.is_valid():
            context_data = {'form': public_assignment_form,
                            'title': 'Editar de Designação',
                            'button': 'Salvar'}

            return render(request, template_name, context_data)

        public_assignment_form.save()
        messages.success(request, f"Designação do dia {public_assignment_form.cleaned_data['date']} alterada com sucesso")
        return HttpResponseRedirect(r('public-assignment-list'))

    else:
        public_assignment_form = PublicAssignmentForm(instance=instance, request=request)

        context_data = {'form': public_assignment_form,
                        'title': 'Editar de Designação',
                        'button': 'Salvar'}

        return render(request, template_name, context_data)


class ProfileUpdate(UpdateView):
    template_name = 'core/form.html'
    model = Profile
    fields = ['telephone']
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Perfil'
        context['button'] = 'Salvar'
        return context


class CongregationUpdate(UpdateView):
    template_name = 'core/form.html'
    model = Congregation
    fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day', 'random_key']
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Congregação'
        context['button'] = 'Salvar'
        return context


class PersonUpdate(UpdateView):
    model = Person
    template_name = 'core/form.html'
    fields = ['full_name', 'telephone', 'gender', 'privilege', 'modality', 'reader', 'indicator_mic', 'student_parts']
    success_url = reverse_lazy('person-list')
    success_message = "%(full_name)s foi alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Publicador'
        context['button'] = 'Salvar'
        return context


class SpeechUpdate(UpdateView):
    model = Speech
    template_name = 'core/form.html'
    fields = ['number', 'theme']
    success_url = reverse_lazy('speech-list')
    success_message = "O discurso %(number) foi alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Discurso'
        context['button'] = 'Salvar'
        return context
#******************** LIST ********************#
class PersonList(ListView):
    template_name = 'core/list_person.html'
    model = Person

    def get_queryset(self):
        self.object_list = Person.objects.filter(congregation=self.request.user.profile.congregation)
        return self.object_list


class SpeechList(ListView):
    template_name = 'core/list_speech.html'
    model = Speech


class PublicAssignmentList(ListView):
    template_name = 'core/list_public_assignment.html'
    model = PublicAssignment

    def get_queryset(self):
        self.object_list = PublicAssignment.objects.filter(congregation=self.request.user.profile.congregation)
        return self.object_list


#******************** DELETE ********************#
class PersonDelete(DeleteView):
    template_name = 'core/form_delete.html'
    model = Person
    success_url = reverse_lazy('person-list')
    success_message = "O publicador %(full_name)s foi excluído com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Publicador'
        context['button'] = 'Excluir'
        return context


class PublicAssignmentDelete(DeleteView):
    template_name = 'core/form_delete.html'
    model = PublicAssignment
    success_url = reverse_lazy('public-assignment-list')
    success_message = "A designação do dia %(date)s foi excluída com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Designação'
        context['button'] = 'Excluir'
        return context


class SpeechDelete(DeleteView):
    template_name = 'core/form_delete.html'
    model = Speech
    success_url = reverse_lazy('speech-list')
    success_message = "O discurso %(number)s foi excluído com sucesso."
    error_url = success_url


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Discurso'
        context['button'] = 'Excluir'
        return context


    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f'Não é possível excluír o Discurso {self.object}, pois está associado a outro registro.')
            return HttpResponseRedirect(self.error_url)
