from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from jwcm.lpw.models import PersonAvailability, CongregationAvailability
from jwcm.lpw.forms import PersonAvailabilityForm, CongregationAvailabilityForm


class PersonAvailabilityUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'form.html'
    model = PersonAvailability
    form_class = PersonAvailabilityForm
    success_url = reverse_lazy('person-list')
    success_message = "Disponibilidade para o TPL alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar disponibilidade do TPL'
        context['button'] = 'Salvar'
        return context


class CongregationAvailabilityUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'form.html'
    model = CongregationAvailability
    form_class = CongregationAvailabilityForm
    success_message = "Disponibilidade para o TPL alterado com sucesso."

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar disponibilidade do TPL da congregação'
        context['button'] = 'Salvar'
        return context

    def get_success_url(self):
        return reverse_lazy("congregation", kwargs={"pk": self.object.id})
