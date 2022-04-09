from django.db import models
from jwcm.core.models import Congregation
from django.contrib.auth.models import User



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