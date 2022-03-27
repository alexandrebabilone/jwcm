from django.db import models
from datetime import time
from django.contrib.auth.models import User
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
    reader = models.BooleanField(default=False, verbose_name='Leitor')
    indicator_mic = models.BooleanField(default=False, verbose_name='Indicador/Microfone')
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


class Profile(models.Model):
    telephone = models.CharField(max_length=16, verbose_name='Telefone', null=True)
    congregation = models.ForeignKey(Congregation, on_delete=models.PROTECT, null=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        if (self.user is not None) and (self.congregation is not None):
            return f'{self.user.first_name} ({self.congregation})'
        else:
            return f'{self.pk}º profile'

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'


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
