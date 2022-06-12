from django.db import models
from jwcm.core.models import AbstractMeeting, Person


class Part(models.Model):
    #time? lesson?
    theme = models.CharField(verbose_name='Tema', max_length=100)
    owner = models.ForeignKey(Person, verbose_name='Dono da parte', on_delete=models.PROTECT, null=True, related_name='owner')
    helper = models.ForeignKey(Person, verbose_name='Ajudante', on_delete=models.PROTECT, null=True, related_name='helper')

class MidweekMeeting(AbstractMeeting):
    parts = models.ManyToManyField(Part, verbose_name='midweek_meeting')

    #TESOUROS DA PALAVRA DE DEUS
    #discurso 10min
    #joias espirituais
    #leitura da biblia

    #FAÇA SEU MELHOR NO MINISTÉRIO
    #1 a 4 partes nessa seção

    #NOSSA VIDA CRISTÃ
    #1 a 3 partes
    #estudo biblico