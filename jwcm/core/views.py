from django.forms import ModelForm, formset_factory, modelformset_factory
from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView, FormView
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.views import View
from jwcm.core.forms import BatchPersonForm, MechanicalPrivileges, MeetingMechanicalPrivilegesForm, BulletinForm
from django.shortcuts import get_object_or_404, render, resolve_url as r
from django.urls import reverse_lazy
from django.contrib import messages
from jwcm.core.models import Congregation, Person, Meeting, PublicAssignment
from jwcm.life_and_ministry.models import Part
from django.contrib.messages.views import SuccessMessageMixin
import pandas as pd
import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus.tables import Table
from reportlab.platypus import SimpleDocTemplate, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet


styles = getSampleStyleSheet()

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

            _batch_read_and_create_person(df_batch, congregation)
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
              'indicator', 'mic', 'note_sound_table', 'zoom_indicator']
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
    fields = ['full_name', 'telephone', 'gender', 'student_parts', 'privilege', 'modality', 'watchtower_reader',
              'bible_study_reader', 'weekend_meeting_president', 'midweek_meeting_president',
              'indicator', 'mic', 'note_sound_table', 'zoom_indicator']
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
    fields = ['date', 'president', 'indicator_1', 'indicator_2', 'mic_1', 'mic_2', 'note_sound_table', 'zoom_indicator']
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
        form.fields['note_sound_table'].queryset = Person.objects.note_sound_tables_per_congregation(
            user_congregation)
        form.fields['zoom_indicator'].queryset = Person.objects.zoom_indicators_per_congregation(
            user_congregation)

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
        self.object_list = Meeting.objects.meetings_per_congregation(congregation=self.request.user.profile.congregation)
        return self.object_list


class MechanicalPrivilegesView(View):
    template_name = 'core/mechanical_privileges.html'
    form_class = MechanicalPrivileges
    success_url = reverse_lazy('home')
    context = {
        'button_1': 'Buscar',
        'button_2': 'Designar Automaticamente',
        'button_3': 'Salvar',
    }

    def get(self, request, *args, **kwargs):
        form_search = self.form_class()
        self.context['form_search'] = form_search
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form_search = self.form_class(request.POST)
        user_congregation = request.user.profile.congregation

        if not form_search.is_valid():
            return render(request, self.template_name, {'form_search': form_search})

        if 'buscar' in request.POST:
            MeetingFormSet = modelformset_factory(model=Meeting,
                                                  form=MeetingMechanicalPrivilegesForm,
                                                  extra=0)
            meetings_qs = Meeting.objects.select_range_per_congregation(
                form_search.cleaned_data['start_date'],
                form_search.cleaned_data['end_date'],
                congregation=user_congregation)

            formset = MeetingFormSet(queryset=meetings_qs) #request.POST or None,

            for _form in formset:
                _form.fields['indicator_1'].queryset = Person.objects.indicators_per_congregation(user_congregation)
                _form.fields['indicator_2'].queryset = _form.fields['indicator_1'].queryset
                _form.fields['mic_1'].queryset = Person.objects.mics_per_congregation(user_congregation)
                _form.fields['mic_2'].queryset = _form.fields['mic_1'].queryset
                _form.fields['note_sound_table'].queryset = Person.objects.note_sound_tables_per_congregation(
                    user_congregation)
                _form.fields['zoom_indicator'].queryset = Person.objects.zoom_indicators_per_congregation(
                    user_congregation)

            self.context['form_search'] = form_search
            self.context['formset'] = formset
            #self.context['meetings'] = meetings

            return render(request, self.template_name, self.context)

        if 'salvar' in request.POST:
            formset = self.context['formset']
            if not formset.is_valid():
                return render(request, self.template_name, self.context)

            formset.save()
            messages.success(request, 'Privilégios designados com sucesso.')
            return HttpResponseRedirect(r('home'))
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

        # partes de estudante
        if row[11].lower() in true_options:
            student_parts = True
        else:
            student_parts = False

        # presidente da reunião de fim de semana
        if row[12].lower() in true_options:
            weekend_meeting_president = True
        else:
            weekend_meeting_president = False

        # presidente da reunião de meio de semana
        if row[13].lower() in true_options:
            midweek_meeting_president = True
        else:
            midweek_meeting_president = False

        person = Person(full_name=full_name, telephone=telephone, gender=gender, privilege=privilege, modality=modality,
                        watchtower_reader=watchtower_reader, bible_study_reader=bible_study_reader,
                        indicator=indicator, mic=mic, note_sound_table=note_sound_table, zoom_indicator=zoom_indicator,
                        weekend_meeting_president=weekend_meeting_president, midweek_meeting_president=midweek_meeting_president,
                        student_parts=student_parts,
                        congregation=congregation)

        list_person.append(person)

    Person.objects.bulk_create(list_person)


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


#******************** REPORTS ********************#
class BulletinBoardView(FormView):
    template_name = 'core/bulletin_board.html'
    form_class = BulletinForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['button_mechanical_privileges'] = 'Privilégios mecânicos'
        context['button_student_parts'] = 'Partes de estudante'
        context['button_midweek_meeting'] = 'Reunião de meio de semana'
        context['button_weekend_meeting'] = 'Reunião de fim de semana'
        context['title'] = 'Relatórios'
        return context


    def post(self, request, *args, **kwargs):
        report_filename = ''
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        meetings = Meeting.objects.select_range_per_congregation(start_date, end_date, self.request.user.profile.congregation)

        buffer = io.BytesIO()
        simple_doc = SimpleDocTemplate(buffer, pagesize=letter, bottomup=0)


        if 'mechanical_privileges' in request.POST:
            table_data = make_table_data_mechanical_privileges_report(meetings)
            make_table_report(simple_doc, table_data, 'Privilégios mecânicos')
            report_filename = f'mechanical_privileges_{start_date}_to_{end_date}.pdf'
        elif 'student_parts' in request.POST:
            make_data_students_parts_report(simple_doc, meetings, 'DESIGNAÇÃO PARA A REUNIÃO NOSSA VIDA E MINISTERIO CRISTÃO')
            report_filename = f'student_parts_{start_date}_to_{end_date}.pdf'
        elif 'midweek_meeting' in request.POST:
            make_data_midweek_meeting_report(simple_doc, meetings, 'Programação da reunião de meio de semana')
            report_filename = f'midweek_meeting_{start_date}_to_{end_date}.pdf'
        else:
            table_data = make_table_data_weekend_meeting_report(meetings)
            make_table_report(simple_doc, table_data, 'Reunião de fim de semana')
            report_filename = f'weekend_meeting__{start_date}_to_{end_date}.pdf'

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=report_filename)
#******************** REPORTS ********************#
def make_table_report(simple_doc, table_data, title):
    report_elements = []
    simple_doc.title = title
    table = Table(table_data)
    table.setStyle(table_style_mechanical_privileges())
    report_elements.append(Paragraph(title, styles['Title']))
    report_elements.append(Spacer(1 * cm, 1 * cm))
    report_elements.append(table)
    simple_doc.build(report_elements)


def table_style_mechanical_privileges():
    return TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])


def make_table_data_weekend_meeting_report(meetings):
    table_data = []
    table_data.append(['Data', 'Orador', 'Discurso', 'Leitor de A Sentinela'])

    for meeting in meetings:
        speaker_name, speech_theme, watchtower_reader = '', '', ''

        if meeting.public_assignment:
            if meeting.public_assignment.speaker:
                speaker_name = meeting.public_assignment.speaker.full_name

            if meeting.public_assignment.speech:
                speech_theme = meeting.public_assignment.speech.theme

            if meeting.watchtower_reader:
                watchtower_reader = meeting.watchtower_reader.full_name

        table_data.append([meeting.date.strftime("%d/%m/%Y"),
                           f'{speaker_name}',
                           f'{speech_theme}',
                           f'{watchtower_reader}'])

    return table_data


def make_table_data_mechanical_privileges_report(meetings):
    table_data = []
    table_data.append(['Data', 'Indicadores', 'Microfones', 'Áudio e vídeo'])

    for meeting in meetings:
        mic_1, mic_2, indicator_1, indicator_2, note, zoom_indicator = '', '', '', '', '', ''

        if meeting.indicator_1:
            indicator_1 = meeting.indicator_1.full_name

        if meeting.indicator_2:
            indicator_2 = meeting.indicator_2.full_name

        if meeting.mic_1:
            mic_1 = meeting.mic_1.full_name

        if meeting.mic_2:
            mic_2 = meeting.mic_2.full_name

        if meeting.note_sound_table:
            note = meeting.note_sound_table.full_name

        if meeting.zoom_indicator:
            zoom_indicator = meeting.zoom_indicator.full_name

        table_data.append([meeting.date.strftime("%d/%m/%Y"), f'{indicator_1} e {indicator_2}',
                           f'{mic_1} e {mic_2}',
                           f'{note} e {zoom_indicator}'])

    return table_data


def table_style_midweek_meeting(list_line_section):
    list_styles = []
    section_colors = [colors.gray, colors.darkgoldenrod, colors.darkred]

    list_styles.append(('ALIGN', (0, 0), (0, -1), 'LEFT'))
    list_styles.append(('ALIGN', (1, 0), (1, -1), 'RIGHT'))
    list_styles.append(('VALIGN', (1, 0), (1, -1), 'TOP'))
    list_styles.append(('FONTSIZE', (0, 0), (-1, -1), 10))
    list_styles.append(('BOTTOMPADDING', (0, 0), (-1, 0), 10))

    for index, section_color in zip(list_line_section, section_colors):
        list_styles.append(('TEXTCOLOR', (0, index), (0, index), colors.white))
        list_styles.append(('BACKGROUND', (0, index), (0, index), section_color))
        list_styles.append(('FONTNAME', (0, index), (0, index), 'Courier-Bold'))

    return TableStyle(list_styles)


def make_data_midweek_meeting_report(simple_doc, meetings, title):
    report_elements = []

    simple_doc.title = title
    report_elements.append(Paragraph(title, styles['Title']))
    report_elements.append(Spacer(1 * cm, 1 * cm))

    for meeting in meetings:
        table_data, section_lines = [], []
        index = 0

        if meeting.is_weekend_meeting():
            continue

        table_data.append([f'{meeting.week if meeting.week else meeting.date.strftime("%d/%m/%Y")} '
                           f'| {meeting.weekly_reading if meeting.weekly_reading else "Leitura semanal da Bíblia"}',
                           f'Presidente: {meeting.president}'])

        if meeting.initial_song:
            table_data.append([meeting.initial_song, ''])

        index += 1
        section_lines.append(index)

        assignments_tesouros = meeting.lifeandministryassignment_set.filter(part__section=Part.TESOUROS_DA_PALAVRA_DE_DEUS)
        assignments_ministerio = meeting.lifeandministryassignment_set.filter(part__section=Part.FACA_SEU_MELHOR_NO_MINISTÉRIO)
        assignments_vida = meeting.lifeandministryassignment_set.filter(part__section=Part.NOSSA_VIDA_CRISTA)

        table_data.append(['TESOUROS DA PALAVRA DE DEUS', ''])
        _populate_table(assignments_tesouros, table_data)
        index += len(assignments_tesouros) + 1
        section_lines.append(index)

        table_data.append(['FAÇA SEU MELHOR NO MINISTÉRIO', ''])
        _populate_table(assignments_ministerio, table_data)
        index += len(assignments_ministerio) + 1
        section_lines.append(index)

        table_data.append(['NOSSA VIDA CRISTÃ', ''])
        if meeting.middle_song:
            table_data.append([meeting.middle_song, ''])
        _populate_table(assignments_vida, table_data)
        index += len(assignments_vida) + 2

        if meeting.final_song:
            table_data.append([meeting.final_song, ''])

        table = Table(table_data, colWidths=(160 * mm, 40 * mm))
        table.setStyle(table_style_midweek_meeting(section_lines))
        report_elements.append(table)
        report_elements.append(PageBreak())

    simple_doc.build(report_elements)


def _populate_table(assignments, table_data):
    people = ''

    for assignment in assignments:
        if assignment.owner:
            people = assignment.owner.full_name

        if assignment.assistant:
            people += '/' + assignment.assistant.full_name

        p = Paragraph(assignment.part.theme, styles["BodyText"])
        table_data.append([p, people])


def make_data_students_parts_report(simple_doc, meetings, title):
    report_elements = []

    simple_doc.title = title
    report_elements.append(Paragraph(title, styles['Title']))
    report_elements.append(Spacer(1 * cm, 1 * cm))

    for meeting in meetings:
        table_data, section_lines = [], []
        index = 0

        if meeting.is_weekend_meeting():
            continue

        assignments_tesouros = meeting.lifeandministryassignment_set.filter(
            part__section=Part.TESOUROS_DA_PALAVRA_DE_DEUS)
        assignments_ministerio = meeting.lifeandministryassignment_set.filter(
            part__section=Part.FACA_SEU_MELHOR_NO_MINISTÉRIO)

        table_data.append(f'Data: {5}')
        table_data.append(f'Designação: {5}')
        table_data.append(f'Observação para o estudante: A liçãoo da brochura Melhore e a fonte de materia para a sua designação estão na Apostila da Reuniao Vida e Ministerio. '
                           'Estude a lição da brochura para saber como aplicar o ponto que voce vai considerar.')


        table = Table(table_data, colWidths=(160 * mm, 40 * mm))
        table.setStyle(table_style_midweek_meeting(section_lines))
        report_elements.append(table)
        report_elements.append(PageBreak())

    simple_doc.build(report_elements)


def _populate_student_pars(assignments, table_data):
    owner, assistant = '', ''

    for assignment in assignments:
        if assignment.owner:
            owner = assignment.owner.full_name

        table_data.append(f'Nome: {owner}')

        if assignment.assistant:
            assistant = assignment.assistant.full_name

        table_data.append(f'Ajudante: {assistant}')

        p = Paragraph(assignment.part.theme, styles["BodyText"])
        table_data.append([p, people])