from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class SubjectAccumulation(DatetimeTrackingModel):
    ogrn = models.CharField(
        db_index=True,
        unique=True,
        max_length=15,
        verbose_name=_('ОГРН (ОГРНИП) клиента'),
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Наименование клиента'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.ogrn} ({self.id})'

    class Meta:
        verbose_name = _('Субъект накопления')
        verbose_name_plural = _('Субъекты накопления')
