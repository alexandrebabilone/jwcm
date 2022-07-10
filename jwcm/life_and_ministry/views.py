from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, ListView
import datetime
import requests
from bs4 import BeautifulSoup
from jwcm.life_and_ministry.models import Part, LifeAndMinistryAssignment



def _verify_parts():
    base_url = 'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{}/{}'
    current_date = datetime.date.today()
    objects_parts = Part.objects.order_by('-date')
    list_parts = []

    if objects_parts:
        initial_date = objects_parts[0].date
    else:
        initial_date = current_date

    # se não houver registros no banco, procura a partir da semana atual até onde der
    for _ in range(10):
        num_year, num_week, num_day = initial_date.isocalendar()
        base_url.format(num_year, num_week)
        html_file = requests.get(base_url).content
        data = BeautifulSoup(html_file, 'html.parser')
        parts = data.find_all("p", class_="so")

        for part in parts:
            theme = part.text
            section = part.find_previous("h2").text
            p = Part(theme=theme, section=section)#, week=current_date)
            list_parts.append(p)

        initial_date = initial_date + datetime.timedelta(weeks=1)

    Part.objects.bulk_create(list_parts)


class PartListView(ListView):
    template_name = 'life_and_ministry/list_part.html'
    model = Part


class AssignmentListView(ListView):
    template_name = 'life_and_ministry/list_assignment.html'
    model = LifeAndMinistryAssignment


class PartUpdate(SuccessMessageMixin, UpdateView):
    model = Part
    template_name = 'life_and_ministry/form.html'
    fields = ['section', 'theme', 'date']
    success_url = reverse_lazy('part-list')
    success_message = "A parte do dia %(date)s foi alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Parte'
        context['button'] = 'Salvar'
        return context


class AssignmentUpdate(SuccessMessageMixin, UpdateView):
    model = LifeAndMinistryAssignment
    template_name = 'life_and_ministry/form.html'
    fields = ['part', 'owner', 'assistant']
    success_url = reverse_lazy('assignment-list')
    success_message = "A designação do dia %(part.date)s foi alterada com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Designação'
        context['button'] = 'Salvar'
        return context
