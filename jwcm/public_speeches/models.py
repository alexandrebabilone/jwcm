from django.db import models
from django.urls import reverse_lazy
from jwcm.core.models import Congregation, Person


class Speech(models.Model):
    number = models.IntegerField(unique=True, verbose_name='Número')
    theme = models.CharField(max_length=80, verbose_name='Tema')

    def __str__(self):
        return f'{self.number} - {self.theme}'

    class Meta:
        verbose_name = 'discurso'
        verbose_name_plural = 'discursos'

    def get_update_url(self):
        return reverse_lazy("speech-update", kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy("speech-delete", kwargs={"pk": self.id})


class PublicAssignment(models.Model):
    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT)
    speech = models.ForeignKey(Speech, on_delete=models.PROTECT, null=True, verbose_name='Discurso')
    speaker = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, verbose_name='Orador')
    date = models.DateField(unique=True, verbose_name='Data')

    def get_update_url(self):
        return reverse_lazy('public-assignment-update', kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy("public-assignment-delete", kwargs={"pk": self.id})

    def __str__(self):
        return f'Designação do dia {self.date}, discurso {self.speech}'