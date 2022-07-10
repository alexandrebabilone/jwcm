from django.db import models
from django.urls import reverse_lazy
from jwcm.core.models import Person, Meeting
from datetime import datetime



class Part(models.Model):
    TESOUROS_DA_PALAVRA_DE_DEUS = 0
    FACA_SEU_MELHOR_NO_MINISTÉRIO = 1
    NOSSA_VIDA_CRISTA = 2

    SECTION = (
        (TESOUROS_DA_PALAVRA_DE_DEUS, 'Tesouros da Palavra de Deus'),
        (FACA_SEU_MELHOR_NO_MINISTÉRIO, 'Faça seu melhor no ministério'),
        (NOSSA_VIDA_CRISTA, 'Nossa vida cristã'),
    )

    section = models.IntegerField(choices=SECTION, default=TESOUROS_DA_PALAVRA_DE_DEUS, verbose_name='Seção')
    theme = models.CharField(verbose_name='Tema', max_length=100)
    date = models.DateField(verbose_name='Data', default=datetime.now)


    def __str__(self):
        return f'Parte da reunião Vida e Ministério: {self.theme} {self.SECTION[self.section][1]}'

    def get_update_url(self):
        return reverse_lazy("part-update", kwargs={"pk": self.id})

    class Meta:
        verbose_name = 'parte'
        verbose_name_plural = 'partes'


class LifeAndMinistryAssignment(models.Model):
    part = models.ForeignKey(Part, on_delete=models.PROTECT, null=True, verbose_name='Parte')
    owner = models.ForeignKey(Person, verbose_name='Dono da parte',
                                  on_delete=models.PROTECT, null=True, related_name='owner')
    assistant = models.ForeignKey(Person, verbose_name='Ajudante',
                                  on_delete=models.PROTECT, null=True,
                                  related_name='helper')
    meeting = models.ManyToManyField(Meeting, verbose_name='Reunião')

    def __str__(self):
        return f'Designação da reunião Vida e Ministério: {self.owner} {self.part.theme}'

    def get_update_url(self):
        return reverse_lazy("assignment-update", kwargs={"pk": self.id})

    class Meta:
        verbose_name = 'Designação da reunião Vida e Ministério'
        verbose_name_plural = 'Designações da reunião Vida e Ministério'
