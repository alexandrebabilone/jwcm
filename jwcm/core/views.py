from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from jwcm.core.forms import BatchPersonForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Person
from django.contrib.messages.views import SuccessMessageMixin
import pandas as pd


class Home(TemplateView):
    template_name = 'home.html'


class About(TemplateView):
    template_name = 'about.html'

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
#******************** UPDATE ********************#
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
#******************** LIST ********************#
class PersonList(ListView):
    template_name = 'core/list_person.html'
    model = Person

    def get_queryset(self):
        self.object_list = Person.objects.filter(congregation=self.request.user.profile.congregation)
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
