from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from jwcm.core.forms import BatchPersonForm
from django.shortcuts import render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Person, Meeting, PublicAssignment
from jwcm.lpw.models import PersonAvailability
from django.contrib.messages.views import SuccessMessageMixin
import pandas as pd
import datetime
from jwcm.core.batch import batch_read_and_create_person




def home(request):
    template_name = 'home.html'
    _verify_weekend_meetings(request.user.profile.congregation)
    return render(request, template_name)


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

            batch_read_and_create_person(df_batch, congregation)
            return HttpResponseRedirect(r('person-list'))

        except Exception as e:
                messages.error(request, "Não foi possível abrir o arquivo. " + repr(e))
                return HttpResponseRedirect(r('person-list'))
#******************** CREATE ********************#
class PersonCreate(SuccessMessageMixin, CreateView):
    model = Person
    template_name = 'core/form.html'
    fields = ['full_name', 'telephone', 'gender', 'student_parts', 'privilege', 'modality', 'watchtower_reader',
              'bible_study_reader', 'weekend_meeting_president', 'midweek_meeting_president',
              'indicator', 'mic', 'note_sound_table']
    success_url = reverse_lazy('person-list')


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Registrar Publicador'
        context['button'] = 'Salvar'
        return context

    def form_valid(self, form):
        # antes do "super" o objeto não foi criado nem salvo no banco
        form.instance.congregation = self.request.user.profile.congregation
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        #após salvar o objeto no banco, crio o objeto relacionado à ele para cada dia da semana
        for weekday in range(0,7):
            person_availability = PersonAvailability.objects.create(weekday=weekday, morning=False, afternoon=False, night=False)
            person_availability.person.add(self.object)

        return f'O publicador {self.object.full_name} foi registrado com sucesso.'
#******************** UPDATE ********************#
class CongregationUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'core/congregation_update.html'
    model = Congregation
    fields = ['name', 'number', 'midweek_meeting_day', 'midweek_meeting_time', 'weekend_meeting_day', 'weekend_meeting_time']
    success_url = reverse_lazy('home')
    success_message = "Congregação alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Dados da Congregação'
        context['button'] = 'Salvar'
        return context


class PersonUpdate(SuccessMessageMixin, UpdateView):
    model = Person
    template_name = 'core/person_update.html'
    fields = ['full_name', 'telephone', 'gender', 'student_parts', 'privilege', 'modality', 'watchtower_reader',
              'bible_study_reader', 'weekend_meeting_president', 'midweek_meeting_president',
              'indicator', 'mic', 'note_sound_table']
    success_url = reverse_lazy('person-list')
    success_message = "O registro de %(full_name)s foi alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Publicador'
        context['button'] = 'Salvar'
        return context


class MechanicalPrivilegesUpdateView(SuccessMessageMixin, UpdateView):
    model = Meeting
    template_name = 'core/form.html'
    fields = ['date', 'president', 'indicator_1', 'indicator_2', 'mic_1', 'mic_2', 'note_sound_table']
    success_url = reverse_lazy('mechanical-privileges-list')
    success_message = "Os privilégios da reunião de %(date)s foram alterados com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar designações da reunião'
        context['button'] = 'Salvar'
        return context

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        user_congregation = self.request.user.profile.congregation
        form.fields['date'].disabled = True
        form.fields['president'].queryset = Person.objects.elders_per_congregation(user_congregation)
        form.fields['indicator_1'].queryset = Person.objects.indicators_per_congregation(user_congregation)
        form.fields['indicator_2'].queryset = form.fields['indicator_1'].queryset
        form.fields['mic_1'].queryset = Person.objects.mics_per_congregation(user_congregation)
        form.fields['mic_2'].queryset = form.fields['mic_1'].queryset
        form.fields['note_sound_table'].queryset = Person.objects.note_sound_tables_per_congregation(user_congregation)

        return form
#******************** LIST ********************#
class PersonList(ListView):
    template_name = 'core/list_person.html'
    model = Person

    def get_queryset(self):
        self.object_list = Person.objects.filter(congregation=self.request.user.profile.congregation)
        return self.object_list


class MechanicalPrivilegesListView(ListView):
    template_name = 'core/mechanical_privileges.html'
    model = Meeting

    def get_queryset(self):
        self.object_list = Meeting.objects.meetings_per_congregation_asc(congregation=self.request.user.profile.congregation)
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

#******************** Auxs methods ********************#
def _verify_weekend_meetings(congregation):
    """
     O objetivo dessa função é garantir a criação de reuniões de fim de semana.
     Quando não houver nenhuma reunião cadastrada (apenas na primeira vez), serão criadas reuniões para as próximas 25 semanas.
     Quaando houver reuniões cadastradas, a cada 30 dias (ou por volta de), serão criadas reuniões para as próximas 5 semanas.
    """
    NUM_WEEKS_FIRST = 25
    NUM_WEEKS_AFTER = 5

    current_date = datetime.date.today()

    weekend_day = congregation.weekend_meeting_day
    objects_meetings = Meeting.objects.filter(congregation=congregation).order_by('-date')

    if objects_meetings:
        date_last_meeting = objects_meetings[0].date

        if (date_last_meeting - current_date).days < 145:
            initial_date = date_last_meeting + datetime.timedelta(weeks=1)
            _create_weekend_meetings(initial_date, NUM_WEEKS_AFTER, Meeting.WEEKEND, congregation)
    else:
        initial_date = _get_first_weekend_meeting_day_of_month(current_date, weekend_day)
        _create_weekend_meetings(initial_date, NUM_WEEKS_FIRST, Meeting.WEEKEND, congregation)


def _create_weekend_meetings(initial_date, num_of_meetings, type_of_meeting, congregation):
    list_meetings = []

    for _ in range(num_of_meetings):
        weekend_meeting = Meeting(date=initial_date, congregation=congregation, type=type_of_meeting,
                                  public_assignment=PublicAssignment.objects.create(speech=None, speaker=None))
        list_meetings.append(weekend_meeting)
        initial_date += datetime.timedelta(weeks=1)

    Meeting.objects.bulk_create(list_meetings)


def _get_first_weekend_meeting_day_of_month(some_date, weekend_day):
    current_month = some_date.month
    current_year = some_date.year
    first_weekend_meeting_day_of_month = datetime.date(current_year, current_month, 1)

    while first_weekend_meeting_day_of_month.weekday() != weekend_day:
        first_weekend_meeting_day_of_month += datetime.timedelta(days=1)

    return first_weekend_meeting_day_of_month
"""
def mechanical_TODO(request):
    form = MechanicalPrivilegesForm(request.POST or None)
    template_name = 'core/mechanical_todo.html'
    congregation = request.user.profile.congregation
    meetings = []


    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        meetings = Meeting.objects.select_range_per_congregation(start_date, end_date, congregation)



    return render(request, template_name, {'form': form, 'button_search': 'Buscar', 'title': 'Privilégios mecânicos', 'meetings': meetings})
"""