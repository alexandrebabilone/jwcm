import re
import time
import datetime
import requests
from bs4 import BeautifulSoup
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, ListView
from jwcm.life_and_ministry.models import Part, LifeAndMinistryAssignment
from jwcm.core.models import Meeting, Person, Congregation


class PartListView(ListView):
    template_name = 'life_and_ministry/list_part.html'
    model = Part

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.verify_parts()
        self.verify_midweek_meetings(self.request.user.profile.congregation)
        return context

    def verify_parts(self):
        """
        O objetivo dessa função é verificar a necessidade de puxar/criar as partes (Part).
        Se é a primeira vez que vamos puxar as partes, procuramos as próximas 20 partes a partir da semana atual.
        Senão,
        """
        NUM_WEEKS_FIRST = 20
        NUM_WEEKS_AFTER = 10

        objects_parts = Part.objects.sorted_by_date_desc()
        current_date = datetime.date.today()

        if not objects_parts:
            date_of_first_day_of_week = _get_date_of_first_day_of_week(current_date)
            self.parts_scraping(date_of_first_day_of_week, NUM_WEEKS_FIRST)
        else:
            last_part_date = objects_parts[0].date

            if (last_part_date - current_date).days < 45:
                next_week = last_part_date + datetime.timedelta(weeks=1)
                self.parts_scraping(next_week, NUM_WEEKS_AFTER)

    # tempo total sem thread: >>>> 92.3322856426239 segundos
    # tempo total com thread: >>>>  segundos
    # TODO erro em produção: reunião duplicada sendo criada. DETAIL:  Key (date, congregation_id)=(2022-09-28, 1) already exists.
    # TODO criação das parts em nova congregação - as parts ja existem, as reunioes nao
    def parts_scraping(self, initial_date, num_of_weeks):
        """
        O objetivo dessa função é puxar as partes do site e armazenar no banco.
        """
        not_parts = "Comentários iniciais", "Comentários finais", "Cântico \d{1,3}"
        part_list = []

        for _ in range(num_of_weeks):
            num_year, num_week, num_day = initial_date.isocalendar()
            base_url = 'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{}/{}'
            base_url = base_url.format(num_year, num_week)
            html_file = requests.get(base_url).content
            data = BeautifulSoup(html_file, 'html.parser')

            # Se a busca esta sendo feita em uma semana que ainda não existe programação, aborta a busca
            if data.find(id='p1') and data.find(id='p2'):

                parts = data.find_all("p", class_="so")

                for part in parts:
                    is_part = True
                    theme = part.text.replace(u'\xa0', u' ')

                    for not_part in not_parts:
                        if re.findall(not_part, theme):
                            is_part = False
                            break

                    if not is_part:
                        continue

                    str_section = part.find_previous("h2").text
                    int_section = _set_section(str_section)
                    new_part = Part(theme=theme, section=int_section, date=initial_date)
                    part_list.append(new_part)

            initial_date += datetime.timedelta(weeks=1)

        Part.objects.bulk_create(part_list)


    def verify_midweek_meetings(self, congregation):
        parts = Part.objects.sorted_by_date_desc()

        part_dates = Part.objects.part_dates()
        if not part_dates:
            return

        midweek_meetings = Meeting.objects.midweek_meetings_per_congregation_desc(congregation)
        if midweek_meetings:
            len_part_dates = len(part_dates)
            len_midweek_meetings = len(midweek_meetings)

            if len_part_dates > len_midweek_meetings:
                self.create_meetings_and_assignments(part_dates[:(len_part_dates-len_midweek_meetings)], parts, congregation)
        else:
            self.create_meetings_and_assignments(part_dates, parts, congregation)


    def create_meetings_and_assignments(self, list_of_dates, parts, congregation):
        for date in list_of_dates:
            # TODO: maneira mais elegante de pegar as datas
            meeting_date = _get_midweek_meeting_day_of_week(date['date'], congregation.midweek_meeting_day)
            new_meeting = Meeting.objects.create(date=meeting_date, congregation=congregation,
                                                 type=Meeting.MIDWEEK)  # , week=week, weekly_reading=weekly_reading

            filtered_parts = filter(lambda part: part.date == date['date'], parts)
            filtered_parts = list(filtered_parts)

            for part in filtered_parts:
                new_assignment = LifeAndMinistryAssignment.objects.create(owner=None, assistant=None, part=part)
                new_assignment.meeting.add(new_meeting)


class AssignmentListView(ListView):
    template_name = 'life_and_ministry/list_assignment.html'
    model = LifeAndMinistryAssignment

    def get_queryset(self):
        list_assignments = []
        meetings = Meeting.objects.midweek_meetings_per_congregation_desc(self.request.user.profile.congregation)

        for meeting in meetings:
            list_assignments.extend(meeting.lifeandministryassignment_set.all())
        self.object_list = list_assignments
        return self.object_list


class PartUpdate(SuccessMessageMixin, UpdateView):
    model = Part
    template_name = 'life_and_ministry/form.html'
    fields = ['date', 'section', 'theme']
    success_url = reverse_lazy('part-list')
    success_message = "A parte do dia %(date)s foi alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Parte'
        context['button'] = 'Salvar'
        return context

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['date'].disabled = True
        return form


class AssignmentUpdate(SuccessMessageMixin, UpdateView):
    model = LifeAndMinistryAssignment
    template_name = 'life_and_ministry/form.html'
    fields = ['part', 'owner', 'assistant']
    success_url = reverse_lazy('assignment-list')
    success_message = "A designação: %(part)s foi alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Designação'
        context['button'] = 'Salvar'
        return context

    def get_form(self, *args, **kwargs):
        congregation = self.request.user.profile.congregation
        form = super().get_form(*args, **kwargs)
        section = form.instance.part.section

        form.fields['part'].disabled = True
        form.fields['assistant'].required = False

        #Definir as queries de acordo com as partes
        if section == Part.TESOUROS_DA_PALAVRA_DE_DEUS:
            if 'Leitura da Bíblia' in form.instance.part.theme:
                form.fields['owner'].queryset = Person.objects.men_student_parts_per_congregation(congregation)
            else:
                form.fields['owner'].queryset = Person.objects.elders_and_ministerial_servants_per_congregation(congregation)
        elif section == Part.FACA_SEU_MELHOR_NO_MINISTÉRIO:
            if 'Vídeo' in form.instance.part.theme:
                form.fields['owner'].queryset = Person.objects.elders_and_ministerial_servants_per_congregation(congregation)
            elif 'Discurso:' in form.instance.part.theme:
                form.fields['owner'].queryset = Person.objects.men_student_parts_per_congregation(congregation)
            else:
                form.fields['owner'].queryset = Person.objects.student_parts_per_congregation(congregation)
                form.fields['assistant'].queryset = Person.objects.student_parts_per_congregation(congregation)
                form.fields['assistant'].required = True
        else:
            form.fields['owner'].queryset = Person.objects.elders_and_ministerial_servants_per_congregation(congregation)
            form.fields['assistant'].queryset = Person.objects.bible_study_readers_per_congregation(congregation)


        return form


def _set_section(str_section):
    if str_section == "TESOUROS DA PALAVRA DE DEUS":
        int_section = Part.TESOUROS_DA_PALAVRA_DE_DEUS
    elif str_section == "FAÇA SEU MELHOR NO MINISTÉRIO":
        int_section = Part.FACA_SEU_MELHOR_NO_MINISTÉRIO
    else:
        int_section = Part.NOSSA_VIDA_CRISTA

    return int_section


def _get_first_midweek_meeting_day_of_month(some_date, midweek_day):
    current_month = some_date.month
    current_year = some_date.year
    first_midweek_meeting_day_of_month = datetime.date(current_year, current_month, 1)

    while first_midweek_meeting_day_of_month.weekday() != midweek_day:
        first_midweek_meeting_day_of_month -= datetime.timedelta(days=1)

    return first_midweek_meeting_day_of_month


def _get_date_of_first_day_of_week(some_date):
    while some_date.weekday() != 0: #0 representa segunda-feira
        some_date -= datetime.timedelta(days=1)

    return some_date


def _get_midweek_meeting_day_of_week(some_date, midweek_meeting_day):
    while some_date.weekday() != midweek_meeting_day:
        some_date += datetime.timedelta(days=1)

    return some_date