from django.core.management.utils import get_random_secret_key
from django.db.models.deletion import ProtectedError
from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from jwcm.core.forms import CongregationChoiceForm, UserForm, CongregationForm, PublicAssignmentForm, BatchPersonForm, \
    PersonGuestForm, CongregationGuestPopUpForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Profile, Person, Speech, PublicAssignment
from django.contrib.messages.views import SuccessMessageMixin
import pandas as pd


class Home(TemplateView):
    template_name = 'home.html'


class About(TemplateView):
    template_name = 'about.html'
#******************** POP UP ********************#
def person_guest_create(request):
    form = PersonGuestForm(request.POST or None)

    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(r('person-list'))

    return render(request, 'core/person_guest.html', {'form': form, 'title': 'Cadastrar orador visitante', 'button': 'Salvar'})


def congregation_guest_pop_up_create(request):
    form = CongregationGuestPopUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_congregation");</script>' % (instance.pk, instance))

    return render(request, "core/congregation_guest.html", {'form': form, 'title': 'Cadastrar congregação do orador visitante', 'button': 'Salvar'})
#******************** BATCH CREATE ********************#
def person_batch_create(request):
    template_name = 'core/batch_person.html'
    batch_form = BatchPersonForm(request.POST or None, request.FILES or None)

    if request.method == 'GET':
        context = {
            'button': 'Carregar',
            'title': 'Cadastrar publicadores em lote',
            'form': batch_form}

        return render(request, template_name, context)
    else:
        congregation = request.user.profile.congregation

        try:
            uploaded_file = request.FILES['file']

            if uploaded_file.multiple_chunks():
                messages.error(request, "O arquivo é muito grande (%.2f MB)." % (uploaded_file.size / (1000 * 1000),))
                return HttpResponseRedirect(r('person-batch-create'))

            if uploaded_file.name.endswith('.csv'):
                df_batch = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods', 'odt')):
                df_batch = pd.read_excel(uploaded_file)
            else:
                messages.error(request, 'O formato do arquivo não é válido. Use um arquivo do tipo .csv, .xls ou .xlsx, por exemplo.')
                return HttpResponseRedirect(r('person-batch-create'))

            _batch_read_and_create_person(df_batch, congregation)
            return HttpResponseRedirect(r('person-list'))

        except Exception as e:
                messages.error(request, "Não foi possível abrir o arquivo. " + repr(e))
                return HttpResponseRedirect(r('person-list'))


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
                congregation_form.instance.host = True
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
        messages.success(request, f'Designação do dia {_format_date(public_assignment_form.cleaned_data["date"])} criada com sucesso.')
        return HttpResponseRedirect(r('public-assignment-list'))
    else:
        context_data = {'form': public_assignment_form,
                        'title': 'Designação',
                        'button': 'Cadastrar'}

        return render(request, template_name, context_data)


class PersonCreate(SuccessMessageMixin, CreateView):
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


class SpeechCreate(SuccessMessageMixin, CreateView):
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
        messages.success(request, f"Designação do dia {_format_date(public_assignment_form.cleaned_data['date'])} alterada com sucesso")
        return HttpResponseRedirect(r('public-assignment-list'))

    else:
        public_assignment_form = PublicAssignmentForm(instance=instance, request=request)

        context_data = {'form': public_assignment_form,
                        'title': 'Editar de Designação',
                        'button': 'Salvar'}

        return render(request, template_name, context_data)


class ProfileUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'core/form.html'
    model = Profile
    fields = ['telephone']
    success_url = reverse_lazy('home')
    success_message = "Perfil alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Perfil'
        context['button'] = 'Salvar'
        return context


class CongregationUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'core/form.html'
    model = Congregation
    fields = ['name', 'number', 'midweek_meeting_time', 'weekend_meeting_time', 'midweek_meeting_day', 'weekend_meeting_day']
    success_url = reverse_lazy('home')
    success_message = "Congregação alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Congregação'
        context['button'] = 'Salvar'
        return context


class PersonUpdate(SuccessMessageMixin, UpdateView):
    model = Person
    template_name = 'core/form.html'
    fields = ['full_name', 'telephone', 'gender', 'privilege', 'modality', 'reader', 'indicator_mic', 'student_parts']
    success_url = reverse_lazy('person-list')
    success_message = "O registro de %(full_name)s foi alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Publicador'
        context['button'] = 'Salvar'
        return context


class SpeechUpdate(SuccessMessageMixin, UpdateView):
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
class PersonDelete(SuccessMessageMixin, DeleteView):
    template_name = 'core/form_delete.html'
    model = Person
    success_url = reverse_lazy('person-list')


    def get_success_message(self, cleaned_data):
        return f'O publicador {self.object.full_name} foi excluído com sucesso.'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Publicador'
        context['button'] = 'Excluir'
        return context


class PublicAssignmentDelete(SuccessMessageMixin, DeleteView):
    template_name = 'core/form_delete.html'
    model = PublicAssignment
    success_url = reverse_lazy('public-assignment-list')


    def get_success_message(self, cleaned_data):
        return f'A designação do dia {_format_date(self.object.date)} foi excluída com sucesso.'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Designação'
        context['button'] = 'Excluir'
        return context


class SpeechDelete(SuccessMessageMixin, DeleteView):
    template_name = 'core/form_delete.html'
    model = Speech
    success_url = reverse_lazy('speech-list')
    error_url = success_url

    def get_success_message(self, cleaned_data):
        return f'O discurso {self.object.number} foi excluído com sucesso.'


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


#******************** AUX FUNCTIONS ********************#
def _format_date(date):
    return date.strftime("%d/%m/%Y")


def _batch_read_and_create_person(df_batch, congregation):
    list_person = []

    for index, row in df_batch.iterrows():
        full_name = row[0]
        telephone = row[1]

        if row[2].lower() == 'masculino':
            gender = Person.MASCULINO
        else:
            gender = Person.FEMININO

        if row[3].lower() in ('anciao', 'ancião'):
            privilege = Person.ANCIAO
        elif row[3].lower() in ('servo ministerial'):
            privilege = Person.SERVO_MINISTERIAL
        else:
            privilege = Person.SEM_PRIVILEGIO_ESPECIAL

        if row[4].lower() == 'pioneiro especial':
            modality = Person.PIONEIRO_ESPECIAL
        elif row[4].lower() == 'pioneiro regular':
            modality = Person.PIONEIRO_REGULAR
        elif row[4].lower() == 'pioneiro auxiliar':
            modality = Person.PIONEIRO_AUXILIAR
        else:
            modality = Person.PUBLICADOR

        if row[5].lower() == 'sim':
            reader = True
        else:
            reader = False

        if row[6].lower() == 'sim':
            indicator_mic = True
        else:
            indicator_mic = False

        if row[7].lower() == 'sim':
            student_parts = True
        else:
            student_parts = False

        person = Person(full_name=full_name, telephone=telephone, gender=gender, privilege=privilege, modality=modality,
                        reader=reader, indicator_mic=indicator_mic, student_parts=student_parts,
                        congregation=congregation)

        list_person.append(person)

    Person.objects.bulk_create(list_person)
