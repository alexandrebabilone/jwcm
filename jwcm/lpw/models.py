from django.db import models
from django.urls import reverse_lazy
from jwcm.core.models import Person, Congregation


class Availability(models.Model):
    sunday_morning = models.BooleanField(default=False, verbose_name='Domingo - manhã')
    sunday_afternoon = models.BooleanField(default=False, verbose_name='Domingo - tarde')
    sunday_night = models.BooleanField(default=False, verbose_name='Domingo - noite')

    monday_morning = models.BooleanField(default=False, verbose_name='Segunda - manhã')
    monday_afternoon = models.BooleanField(default=False, verbose_name='Segunda - tarde')
    monday_night = models.BooleanField(default=False, verbose_name='Segunda - noite')

    tuesday_morning = models.BooleanField(default=False, verbose_name='Terça - manhã')
    tuesday_afternoon = models.BooleanField(default=False, verbose_name='Terça - tarde')
    tuesday_night = models.BooleanField(default=False, verbose_name='Terça - noite')

    wednesday_morning = models.BooleanField(default=False, verbose_name='Quarta - manhã')
    wednesday_afternoon = models.BooleanField(default=False, verbose_name='Quarta - tarde')
    wednesday_night = models.BooleanField(default=False, verbose_name='Quarta - noite')

    thursday_morning = models.BooleanField(default=False, verbose_name='Quinta - manhã')
    thursday_afternoon = models.BooleanField(default=False, verbose_name='Quinta - tarde')
    thursday_night = models.BooleanField(default=False, verbose_name='Quinta - noite')

    friday_morning = models.BooleanField(default=False, verbose_name='Sexta - manhã')
    friday_afternoon = models.BooleanField(default=False, verbose_name='Sexta - tarde')
    friday_night = models.BooleanField(default=False, verbose_name='Sexta - noite')

    saturday_morning = models.BooleanField(default=False, verbose_name='Sábado - manhã')
    saturday_afternoon = models.BooleanField(default=False, verbose_name='Sábado - tarde')
    saturday_night = models.BooleanField(default=False, verbose_name='Sábado - noite')

    class Meta:
        abstract = True
        verbose_name = 'Publicador - Disponibilidade TPL'
        verbose_name_plural = 'Publicadores - Disponibilidades TPL'


class PersonAvailability(Availability):
    lpw = models.OneToOneField(Person, on_delete=models.PROTECT, default=None, null=True)

    def get_update_url(self):
        return reverse_lazy("lpw-person-update", kwargs={"pk": self.id})

    class Meta:
        verbose_name = 'Publicador - Disponibilidade TPL'
        verbose_name_plural = 'Publicadores - Disponibilidades TPL'


class CongregationAvailability(Availability):
    lpw = models.OneToOneField(Congregation, on_delete=models.PROTECT, default=None, null=True)

    def get_update_url(self):
        return reverse_lazy("lpw-congregation-update", kwargs={"pk": self.id})

    class Meta:
        verbose_name = 'Congregação - Disponibilidade TPL'
        verbose_name_plural = 'Congregações - Disponibilidades TPL'


class MonthLPW(models.Model):
    pass
    '''one_morning = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)
    one_afternoon = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)
    one_night = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)

    two_morning = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)
    two_afternoon = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)
    two_night = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)'''
