import re
import time
import datetime
import requests
from bs4 import BeautifulSoup
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, ListView
from jwcm.life_and_ministry.models import Part, LifeAndMinistryAssignment
from jwcm.core.models import Meeting


# tempo total sem thread: >>>> 92.3322856426239 segundos
# tempo total com thread: >>>>  segundos
def _verify_midweek_meetings(congregation):
    """
    O objetivo dessa função é puxar as partes do site, e a partir delas criar as reuniões de meio de semana.
    """
    NUM_WEEKS_FIRST = 20
    NUM_WEEKS_AFTER = 10

    midweek_day = congregation.midweek_meeting_day
    current_date = datetime.date.today()
    objects_parts = Part.objects.order_by('-date')

    # caso existam registros no banco com menos de 45 dias, procura as partes a partir da semana seguinte à última
    if objects_parts:
        last_part_date = objects_parts[0].date

        if (last_part_date - current_date).days < 45:
            initial_date = last_part_date + datetime.timedelta(weeks=1)
            _parts_scraping(initial_date, NUM_WEEKS_AFTER, congregation)
    # se não houver registros no banco, procura as partes a partir da semana atual
    else:
        initial_date = _get_first_midweek_meeting_day_of_month(current_date, midweek_day)
        _parts_scraping(initial_date, NUM_WEEKS_FIRST, congregation)

#TODO erro em produção: reunião duplicada sendo criada. DETAIL:  Key (date, congregation_id)=(2022-09-28, 1) already exists.
def _parts_scraping(initial_date, num_of_weeks, congregation):
    not_parts = "Cântico \d{1,3}", "Comentários iniciais", "Comentários finais"
    start_time = time.time()

    for _ in range(num_of_weeks):
        new_meeting = Meeting.objects.create(date=initial_date, congregation=congregation, type=Meeting.MIDWEEK)

        num_year, num_week, num_day = initial_date.isocalendar()
        base_url = 'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{}/{}'
        base_url = base_url.format(num_year, num_week)
        html_file = requests.get(base_url).content
        data = BeautifulSoup(html_file, 'html.parser')
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
            new_part = Part.objects.create(theme=theme, section=int_section, date=initial_date)
            new_assignment = LifeAndMinistryAssignment.objects.create(owner=None, assistant=None, part=new_part)
            new_assignment.meeting.add(new_meeting)
            print(new_assignment)


        initial_date += datetime.timedelta(weeks=1)

    total_time = time.time() - start_time
    print(f' ---------->>>> {total_time}')


class PartListView(ListView):
    template_name = 'life_and_ministry/list_part.html'
    model = Part

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        _verify_midweek_meetings(self.request.user.profile.congregation)
        return context


class AssignmentListView(ListView):
    template_name = 'life_and_ministry/list_assignment.html'
    model = LifeAndMinistryAssignment


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
        form = super().get_form(*args, **kwargs)
        form.fields['part'].disabled = True
        form.fields['assistant'].required = False
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
