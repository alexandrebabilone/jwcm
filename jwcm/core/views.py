from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from jwcm.core.forms import BatchPersonForm, HomeForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Person, AbstractMeeting
from django.contrib.messages.views import SuccessMessageMixin
import pandas as pd
import datetime
from jwcm.life_and_ministry.models import MidweekMeeting
from jwcm.public_speeches.models import WeekendMeeting


def home(request):
    template_name = 'home.html'
    home_form = HomeForm(request.POST or None)

    _verify_meetings(request.user.profile.congregation)

    return render(request, template_name, {'form': home_form})


class Home(TemplateView):
    template_name = 'home.html'
    #_verify_meetings('user_congregation')


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
    template_name = 'core/form.html'
    fields = ['full_name', 'telephone', 'gender', 'student_parts', 'privilege', 'modality', 'watchtower_reader', 'bible_study_reader',
              'indicator', 'mic', 'note_sound_table', 'zoom_indicator']
    success_url = reverse_lazy('person-list')
    success_message = "O registro de %(full_name)s foi alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Publicador'
        context['button'] = 'Salvar'
        return context


class IndicatorMicUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'core/form.html'
    model = AbstractMeeting
    fields = ['indicator_1', 'indicator_2', 'mic_1', 'mic_2']
    #success_url = reverse_lazy('person-list')
    #success_message = "%(full_name)s foi registrado com sucesso."
#******************** LIST ********************#
class PersonList(ListView):
    template_name = 'core/list_person.html'
    model = Person

    def get_queryset(self):
        self.object_list = Person.objects.filter(congregation=self.request.user.profile.congregation)
        return self.object_list


class IndicatorMicList(ListView):
    pass
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
    true_options = 'sim', 's'
    anciao_options = 'anciao', 'ancião', 'a'
    sm_oprtions = 'servo ministerial', 'sm'
    pe_options = 'pioneiro especial', 'pe'
    pr_options = 'pioneiro regular', 'pr'
    pa_options = 'pioneiro auxiliar', 'pa'

    for index, row in df_batch.iterrows():
        full_name = row[0]
        telephone = row[1]

        if row[2].lower() in ('masculino', 'm'):
            gender = Person.MASCULINO
        else:
            gender = Person.FEMININO

        if row[3].lower() in anciao_options:
            privilege = Person.ANCIAO
        elif row[3].lower() in sm_oprtions:
            privilege = Person.SERVO_MINISTERIAL
        else:
            privilege = Person.SEM_PRIVILEGIO_ESPECIAL

        if row[4].lower() in pe_options:
            modality = Person.PIONEIRO_ESPECIAL
        elif row[4].lower() in pr_options:
            modality = Person.PIONEIRO_REGULAR
        elif row[4].lower() in pa_options:
            modality = Person.PIONEIRO_AUXILIAR
        else:
            modality = Person.PUBLICADOR

        #leitor de A Sentinela
        if row[5].lower() in true_options:
            watchtower_reader = True
        else:
            watchtower_reader = False

        # leitor de Estudo Bíblico
        if row[6].lower() in true_options:
            bible_study_reader = True
        else:
            bible_study_reader = False

        # indicador
        if row[7].lower() in true_options:
            indicator = True
        else:
            indicator = False

        # mic
        if row[8].lower() in true_options:
            mic = True
        else:
            mic = False

        # notebook/mesa de som
        if row[9].lower() in true_options:
            note_sound_table = True
        else:
            note_sound_table = False

        # indicador zoom
        if row[10].lower() in true_options:
            zoom_indicator = True
        else:
            zoom_indicator = False

        if row[9].lower() in true_options:
            student_parts = True
        else:
            student_parts = False

        person = Person(full_name=full_name, telephone=telephone, gender=gender, privilege=privilege, modality=modality,
                        watchtower_reader=watchtower_reader, bible_study_reader=bible_study_reader,
                        indicator=indicator, mic=mic, note_sound_table=note_sound_table, zoom_indicator=zoom_indicator,
                        student_parts=student_parts,
                        congregation=congregation)

        list_person.append(person)

    Person.objects.bulk_create(list_person)


def _verify_meetings(user_congregation):
    """
     O objetivo dessa função é garantir que sempre haja reuniões criadas para as próximas 25 semanas
    """
    _verify_meeting(MidweekMeeting, user_congregation.midweek_meeting_day, user_congregation)
    _verify_meeting(WeekendMeeting, user_congregation.weekend_meeting_day, user_congregation)


def _verify_meeting(ClassMeeting, weekday_of_meeting, user_congregation):
    list_meetings = []

    current_date = datetime.date.today()
    current_month = current_date.month
    current_year = current_date.year

    objects_meetings = ClassMeeting.objects.filter(congregation=user_congregation).order_by('-date')

    # se não existe nenhuma reunião cadastrada, criar para as próximas 25 semanas meses a partir do mês corrente
    if not objects_meetings:
        date = datetime.date(current_year, current_month, 1)
        while date.weekday() != weekday_of_meeting:
            date = date + datetime.timedelta(days=1)

        for _ in range(25):
            meeting = ClassMeeting(date=date, congregation=user_congregation)
            list_meetings.append(meeting)
            date = date + datetime.timedelta(days=7)
    # existem reuniões cadastradas, mas não tem mais 5 meses de reunião criados à frente -> então cria mais 5 semanas de reunião
    elif (objects_meetings[0].date - current_date).days < 150:
        date_last_meeting = objects_meetings[0].date

        for _ in range(5):
            date_last_meeting = date_last_meeting + datetime.timedelta(days=7)
            meeting = ClassMeeting(date=date_last_meeting, congregation=user_congregation)
            list_meetings.append(meeting)

    ClassMeeting.objects.bulk_create(list_meetings)
