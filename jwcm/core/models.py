from django.db.models import Q, UniqueConstraint
from django.db import models
from datetime import time
from django.urls import reverse_lazy
from jwcm.core.managers import PersonQuerySet, MeetingQuerySet
from jwcm.public_speeches.models import Speech


class Congregation(models.Model):
    SEGUNDA = 0
    TERCA = 1
    QUARTA = 2
    QUINTA = 3
    SEXTA = 4
    SABADO = 5
    DOMINGO = 6

    DAY_OF_WEEK = (
        (DOMINGO, 'Domingo'),
        (SEGUNDA, 'Segunda-feira'),
        (TERCA, 'Terça-feira'),
        (QUARTA, 'Quarta-feira'),
        (QUINTA, 'Quinta-feira'),
        (SEXTA, 'Sexta-feira'),
        (SABADO, 'Sábado'),
    )

    name = models.CharField(max_length=50, verbose_name='Nome')
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
    weekend_meeting_president = models.BooleanField(default=False, verbose_name='Presidente - Reunião de fim de semana')
    midweek_meeting_president = models.BooleanField(default=False, verbose_name='Presidente - Reunião de meio de semana')
    student_parts = models.BooleanField(default=True, verbose_name='Partes de Estudante')
    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT, null=True)

    def get_update_url(self):
        return reverse_lazy("person-update", kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy("person-delete", kwargs={"pk": self.id})

    @property
    def indicators(self):
        return Meeting.objects.filter(Q(indicator_1=self) | Q(indicator_2=self))

    @property
    def mics(self):
        return Meeting.objects.filter(Q(mic_1=self) | Q(mic_2=self))

    def __str__(self):
        return f'{self.full_name}'

    objects = PersonQuerySet.as_manager()

    class Meta:
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'
        constraints = [UniqueConstraint(fields=['full_name', 'congregation'], name='unique_full_name_per_congregation')]


class PublicAssignment(models.Model):
    speech = models.ForeignKey(Speech, on_delete=models.PROTECT, null=True, verbose_name='Discurso')
    speaker = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, verbose_name='Orador')

    def get_update_url(self):
        return reverse_lazy('public-assignment-update', kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy("public-assignment-delete", kwargs={"pk": self.id})

    def __str__(self):
        return f'Designação pública - {self.speech} - {self.speaker}'

    class Meta:
        verbose_name = 'designação pública'
        verbose_name_plural = 'designações públicas'


class Meeting(models.Model):
    MIDWEEK = 0
    WEEKEND = 1

    MEETING_TYPE = (
        (MIDWEEK, 'Meio de semana'),
        (WEEKEND, 'Fim de semana'),
    )

    type = models.IntegerField(choices=MEETING_TYPE, default=MIDWEEK, verbose_name='Tipo de Reunião')
    date = models.DateField(verbose_name='Data')
    president = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, verbose_name='Presidente')
    indicator_1 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Indicador 1')
    indicator_2 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Indicador 2')
    mic_1 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Microfone 1')
    mic_2 = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Microfone 2')
    note_sound_table = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='audio_video_operator', verbose_name='Notebook/mesa de som')
    zoom_indicator = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='audio_video_indicator', verbose_name='Indicador Zoom')
    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT, verbose_name='Congregação')

    # as partes (relação ManyToMany) foram definidas na classe Parts

    # atributos específicos de reunião de fim de semana
    ruling_watchtower = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Dirigente de A Sentinela')
    reader_watchtower = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='+', verbose_name='Leitor de A Sentinela')
    public_assignment = models.ForeignKey(PublicAssignment, on_delete=models.CASCADE, null=True, verbose_name='Designação Pública')

    objects = MeetingQuerySet.as_manager()

    def __str__(self):
        return f'[{self.date}] - Reunião de {self.MEETING_TYPE[self.type][1]}'

    def get_update_url(self):
        return reverse_lazy('mechanical-privileges-update', kwargs={"pk": self.id})

    class Meta:
        verbose_name = 'reunião'
        verbose_name_plural = 'reuniões'
        constraints = [UniqueConstraint(fields=['date', 'congregation'], name='unique_meeting_per_congregation')]
