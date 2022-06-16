from django.db import models
from django.urls import reverse_lazy



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
