from django.contrib import messages
from django.http import HttpResponseRedirect
from jwcm.core.models import Congregation, Person
from jwcm.lpw.models import PersonAvailability, CongregationAvailability, DayLPW
from jwcm.lpw.forms import SearchMonthlyLPWForm, CongregationAvailabilityForm, PersonAvailabilityForm, DayLPWForm
from django.shortcuts import render, resolve_url as r
import calendar, datetime
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory


def person_availability_update(request, pk):
    template_name = 'lpw_update.html'
    person = Person.objects.get(pk=pk)

    PersonAvailabilityFormSet = modelformset_factory(PersonAvailability, form=PersonAvailabilityForm, extra=0)

    if request.method == 'POST':
        formset = PersonAvailabilityFormSet(request.POST, request.FILES)

        if formset.is_valid():
            formset.save()

        messages.success(request, f"TPL do {person.full_name} alterado com sucesso!")
        return HttpResponseRedirect(r('person-list'))
    else:
        formset = PersonAvailabilityFormSet(queryset=person.personavailability_set.all())
        return render(request, template_name, {'formset': formset})



def congregation_availability_update(request, pk):
    template_name = 'lpw_update.html'
    congregation = Congregation.objects.get(pk=pk)

    CongregationAvailabilityFormSet = modelformset_factory(CongregationAvailability, form=CongregationAvailabilityForm, extra=0)

    if request.method == 'POST':
        formset = CongregationAvailabilityFormSet(request.POST, request.FILES)

        if formset.is_valid():
            formset.save()

        messages.success(request, f"TPL da congregação {congregation.name} alterado com sucesso!")
        return HttpResponseRedirect(r('congregation', pk))
    else:
        formset = CongregationAvailabilityFormSet(queryset=congregation.congregationavailability_set.all())
        return render(request, template_name, {'formset': formset})


#TODO: 1. Mandar uma instancia pra cada form do formset
def monthly_lpw(request):
    congregation = request.user.profile.congregation
    verify_monthly_table_lpw(congregation)
    template_name = 'monthly_lpw.html'

    DayLPWFormSet = modelformset_factory(DayLPW, form=DayLPWForm, extra=0)
    form = SearchMonthlyLPWForm(request.POST or None)

    if 'button_load' in request.POST:
        date_string = request.POST.get('month_and_year')
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

        month, year = date.month, date.year
        number_of_days_in_month = calendar.monthrange(year, month)[1]
        begin_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, number_of_days_in_month)

        formset = DayLPWFormSet(queryset=DayLPW.objects.select_per_congregation_and_month(congregation, begin_date, end_date))

        return render(request, template_name, {'form': form, 'enable_button_save': True, 'formset': formset})
    elif 'button_save' in request.POST:
        formset = DayLPWFormSet(request.POST, request.FILES)

        if formset.is_valid():
            formset.save()

        messages.success(request, f"TPL mensal da congregação {congregation.name} foi alterado com sucesso!")
        return HttpResponseRedirect(r('home'))

    return render(request, template_name, {'form': form, 'enable_button_save': False})




def verify_monthly_table_lpw(congregation):
    """
     Verifica se existe tabela do LPW para os próximos 4 meses (contando o mês atual). Se não tiver, cria para os próximos 4 meses.
    """
    list_new_days_lpw = []
    number_coming_months = 4
    today = datetime.date.today()

    list_coming_months = [today + relativedelta(months=+index) for index in range(number_coming_months)]

    for coming_month in list_coming_months:
        month, year = coming_month.month, coming_month.year
        number_of_days_in_month = calendar.monthrange(year, month)[1]
        begin_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, number_of_days_in_month)

        days_lpw = DayLPW.objects.select_per_congregation_and_month(congregation, begin_date, end_date)

        # verificar se existem registros para aqueles mês
        if not days_lpw:
            # se não existem, gerar a lista de dias do mês
            list_days = [begin_date + datetime.timedelta(days=index) for index in range(number_of_days_in_month)]

            for _day in list_days:
                day_lpw = DayLPW(date=_day, congregation=congregation, weekday=_day.weekday())
                list_new_days_lpw.append(day_lpw)


    if list_new_days_lpw:
        DayLPW.objects.bulk_create(list_new_days_lpw)
