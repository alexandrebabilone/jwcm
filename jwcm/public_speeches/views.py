from django.views.generic import UpdateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, resolve_url as r
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from jwcm.public_speeches.models import Speech, PublicAssignment
from jwcm.public_speeches.forms import PublicAssignmentForm, CongregationGuestPopUpForm, PersonGuestForm



#******************** CREATE ********************#
def public_assignment_create(request):
    template_name = 'public_speeches/form.html'
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


class SpeechCreate(SuccessMessageMixin, CreateView):
    model = Speech
    template_name = 'public_speeches/form.html'
    fields = ['number', 'theme']
    success_url = reverse_lazy('speech-list')
    success_message = "O discurso número %(number)s foi registrado com sucesso."


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Registrar Discurso'
        context['button'] = 'Salvar'
        return context
#******************** LIST ********************#
class PublicAssignmentList(ListView):
    template_name = 'public_speeches/list_public_assignment.html'
    model = PublicAssignment

    def get_queryset(self):
        self.object_list = PublicAssignment.objects.filter(congregation=self.request.user.profile.congregation)
        return self.object_list


class SpeechList(ListView):
    template_name = 'public_speeches/list_speech.html'
    model = Speech
#******************** UPDATE ********************#
class SpeechUpdate(SuccessMessageMixin, UpdateView):
    model = Speech
    template_name = 'public_speeches/form.html'
    fields = ['number', 'theme']
    success_url = reverse_lazy('speech-list')
    success_message = "O discurso %(number) foi alterado com sucesso."


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Atualizar Discurso'
        context['button'] = 'Salvar'
        return context


def public_assignment_update(request, pk):
    template_name = 'public_speeches/form.html'
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
#******************** DELETE ********************#
class SpeechDelete(SuccessMessageMixin, DeleteView):
    template_name = 'public_speeches/form_delete.html'
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


class PublicAssignmentDelete(SuccessMessageMixin, DeleteView):
    template_name = 'public_speeches/form_delete.html'
    model = PublicAssignment
    success_url = reverse_lazy('public-assignment-list')


    def get_success_message(self, cleaned_data):
        return f'A designação do dia {_format_date(self.object.date)} foi excluída com sucesso.'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Excluir Designação'
        context['button'] = 'Excluir'
        return context
#******************** POP UP ********************#
def person_guest_create(request):
    form = PersonGuestForm(request.POST or None)

    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(r('person-list'))

    return render(request, 'public_speeches/person_guest.html', {'form': form, 'title': 'Cadastrar orador visitante', 'button': 'Salvar'})


def congregation_guest_pop_up_create(request):
    form = CongregationGuestPopUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_congregation");</script>' % (instance.pk, instance))

    return render(request, "public_speeches/congregation_guest.html", {'form': form, 'title': 'Cadastrar congregação do orador visitante', 'button': 'Salvar'})


#******************** AUX FUNCTIONS ********************#
def _format_date(date):
    return date.strftime("%d/%m/%Y")