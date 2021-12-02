from enum import Enum

from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeRunningChoices(Enum):
    INTERNAL = ('internal', _('Внутренний'))
    EXTERNAL = ('external', _('Внешний'))

    @classmethod
    def choices(cls):
        return [x.value for x in cls]


class LiabilitiesType(DatetimeTrackingModel):
    name = models.CharField(
        max_length=500,
        verbose_name=_('Наименование вида обязательств'),
    )
    instance = models.ForeignKey(
        'las.Instance',
        on_delete=models.CASCADE,
        verbose_name=_('Идентификатор инстанции'),
    )
    postfix = models.CharField(
        max_length=32,
        verbose_name=_('Постфикс (идентификатор для прямого EVAL-доступа)'),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Основной вид обязательств'),
    )
    type_running = models.CharField(
        max_length=100,
        verbose_name=_('Тип ведения учёта'),
        choices=TypeRunningChoices.choices(),
    )

    def __str__(self):
        return f'{self.name} ({self.id})'

    class Meta:
        verbose_name = _('Вид обязательств')
        verbose_name_plural = _('Виды обязательств')
        constraints = [
            models.UniqueConstraint(fields=['postfix', 'instance'], name='unique')
        ]
