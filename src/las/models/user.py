from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    instance = models.ForeignKey(
        'las.Instance',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('Подучетная инстанция'),
    )

    def __str__(self):
        return f'{self.username} (id: {self.id}, instance: {self.instance})'

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        verbose_name = _('Пользователь: система-клиент API')
        verbose_name_plural = _('Пользователи: системы-клиенты API')
