from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExternalActionProcess(DatetimeTrackingModel):
    liabilities_type = models.ForeignKey(
        'las.LiabilitiesType',
        on_delete=models.CASCADE,
        verbose_name=_('Вид обязательства'),
    )
    action_type = models.ForeignKey(
        'las.ActionType',
        on_delete=models.CASCADE,
        verbose_name=_('Вид действия'),
    )
    url = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name=_('Ссылка вызова внешнего метода'),
    )

    class Meta:
        verbose_name = _('Выполнение внешнего действия')
        verbose_name_plural = _('Выполнения внешних действий')
