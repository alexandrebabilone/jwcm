from django.db import models
from datetime import time
from django.urls import reverse_lazy


class Congregation(models.Model):
    DOMINGO = 0
    SEGUNDA = 1
    TERCA = 2
    QUARTA = 3
    QUINTA = 4
    SEXTA = 5
    SABADO = 6

    DAY_OF_WEEK = (
        (DOMINGO, 'Domingo'),
        (SEGUNDA, 'Segunda-feira'),
        (TERCA, 'Terça-feira'),
        (QUARTA, 'Quarta-feira'),
        (QUINTA, 'Quinta-feira'),
        (SEXTA, 'Sexta-feira'),
        (SABADO, 'Sábado'),
    )

    name = models.CharField(max_length=50, unique=True, verbose_name='Nome')
    number = models.IntegerField(unique=True, verbose_name='Número', null=True)
    midweek_meeting_time = models.TimeField(verbose_name='Horário da reunião de meio de semana',
                                            default=time(19, 30, 00), null=True)
    weekend_meeting_time = models.TimeField(verbose_name='Horário da reunião de fim de semana',
                                            default=time(18, 00, 00), null=True)
    midweek_meeting_day = models.IntegerField(choices=DAY_OF_WEEK, default=QUINTA,
                                              verbose_name='Dia da reunião de meio de semana', null=True)
    weekend_meeting_day = models.IntegerField(choices=DAY_OF_WEEK, default=DOMINGO,
                                              verbose_name='Dia da reunião de fim de semana', null=True)
    host = models.BooleanField(default=False, verbose_name='Congregação Anfitriã')
    random_key = models.CharField(max_length=50, unique=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'congregação'
        verbose_name_plural = 'congregações'


class Person(models.Model):
    MASCULINO = 0
    FEMININO = 1

    GENDER = (
        (MASCULINO, 'Masculino'),
        (FEMININO, 'Feminino'),
    )


    ANCIAO = 0
    SERVO_MINISTERIAL = 1
    SEM_PRIVILEGIO_ESPECIAL = 2

    PRIVILEGE = (
        (ANCIAO, 'Ancião'),
        (SERVO_MINISTERIAL, 'Servo Ministerial'),
        (SEM_PRIVILEGIO_ESPECIAL, 'Sem privilégio especial'),
    )


    PIONEIRO_ESPECIAL = 0
    PIONEIRO_REGULAR = 1
    PIONEIRO_AUXILIAR = 2
    PUBLICADOR = 3

    MODALITY = (
        (PIONEIRO_ESPECIAL, 'Pioneiro Especial'),
        (PIONEIRO_REGULAR, 'Pioneiro Regular'),
        (PIONEIRO_AUXILIAR, 'Pioneiro Auxiliar'),
        (PUBLICADOR, 'Publicador'),
    )

    full_name = models.CharField(max_length=50, null=True, verbose_name='Nome completo')
    telephone = models.CharField(max_length=16, blank=True, verbose_name='Telefone')

    gender = models.IntegerField(choices=GENDER, default=MASCULINO, verbose_name='Sexo')
    privilege = models.IntegerField(choices=PRIVILEGE, default=SEM_PRIVILEGIO_ESPECIAL, verbose_name='Privilégio especial')
    modality = models.IntegerField(choices=MODALITY, default=PUBLICADOR, verbose_name='Ministério')
    watchtower_reader = models.BooleanField(default=False, verbose_name='Leitor de A Sentinela')
    bible_study_reader = models.BooleanField(default=False, verbose_name='Leitor de Estudo Bíblico')
    indicator = models.BooleanField(default=False, verbose_name='Indicador')
    mic = models.BooleanField(default=False, verbose_name='Microfone')
    note_sound_table = models.BooleanField(default=False, verbose_name='Notebook/Mesa de Som')
    zoom_indicator = models.BooleanField(default=False, verbose_name='Indicador Zoom')
    student_parts = models.BooleanField(default=True, verbose_name='Partes de Estudante')

    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT, null=True)

    def get_update_url(self):
        return reverse_lazy("person-update", kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy("person-delete", kwargs={"pk": self.id})

    def __str__(self):
        return f'{self.full_name}'

    class Meta:
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'


class AbstractMeeting(models.Model):
    date = models.DateField(unique=True, verbose_name='Data')
    president = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)
    indicator_1 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    indicator_2 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    mic_1 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    mic_2 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    note_sound_table = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    zoom_indicator = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+')
    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT)

    class Meta:
        abstract = True
