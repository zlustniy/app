from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class ActionType(DatetimeTrackingModel):
    name = models.CharField(
        max_length=50,
        verbose_name=_('Наименование вида действий'),
    )

    def __str__(self):
        return f'{self.name} ({self.id})'

    class Meta:
        verbose_name = _('Вид действия')
        verbose_name_plural = _('Виды действий')
