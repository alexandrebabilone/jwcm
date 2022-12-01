from django.db import models
from django.urls import reverse_lazy
from jwcm.core.models import Person, Congregation
from jwcm.lpw.managers import DayLPWQuerySet


class Availability(models.Model):
    weekday = models.IntegerField(choices=Congregation.DAY_OF_WEEK, default=Congregation.DOMINGO, verbose_name='Dia da semana')
    morning = models.BooleanField(default=False, verbose_name='Manhã')
    afternoon = models.BooleanField(default=False, verbose_name='Tarde')
    night = models.BooleanField(default=False, verbose_name='Noite')

    class Meta:
        abstract = True


class PersonAvailability(Availability):
    person = models.ManyToManyField(Person, verbose_name='Disponibilidade')

    def get_update_url(self):
        return reverse_lazy("lpw-person-update", kwargs={"pk": self.id})

    def __str__(self):
        p = self.person.all()[0]
        return f'{p.full_name} - {Congregation.DAY_OF_WEEK[self.weekday][1]}'

    class Meta:
        verbose_name = 'Publicador - Disponibilidade TPL'
        verbose_name_plural = 'Publicadores - Disponibilidades TPL'


class CongregationAvailability(Availability):
    congregation = models.ManyToManyField(Congregation, verbose_name='Disponibilidade')

    def get_update_url(self):
        return reverse_lazy("lpw-congregation-update", kwargs={"pk": self.id})

    def __str__(self):
        c = self.congregation.all()[0]
        return f'{c.name} - {Congregation.DAY_OF_WEEK[self.weekday][1]}'

    class Meta:
        verbose_name = 'Congregação - Disponibilidade TPL'
        verbose_name_plural = 'Congregações - Disponibilidades TPL'


class DayLPW(models.Model):
    date = models.DateField(verbose_name='Data')
    weekday = models.IntegerField(choices=Congregation.DAY_OF_WEEK, verbose_name='Dia da semana')

    morning = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', blank=True, verbose_name='Manhã')
    morning_available = models.BooleanField(default=False, verbose_name='Disponibilidade - manhã')

    afternoon = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', blank=True, verbose_name='Tarde')
    afternoon_available = models.BooleanField(default=False, verbose_name='Disponibilidade - tarde')

    night = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', blank=True, verbose_name='Noite')
    night_available = models.BooleanField(default=False, verbose_name='Disponibilidade - noite')

    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT, null=True)

    objects = DayLPWQuerySet.as_manager()

    def get_update_url(self):
        return reverse_lazy("lpw-congregation-update", kwargs={"pk": self.id})

    def __str__(self):
        return f'{self.date} ({self.congregation})'

    class Meta:
        verbose_name = 'Dia LPW'
        verbose_name_plural = 'Dias LPW'
