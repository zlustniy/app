from dj_model_utils.abstract_models.datetime_tracking import DatetimeTrackingModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccumulationRegister(DatetimeTrackingModel):
    user = models.ForeignKey(
        'las.User',
        on_delete=models.CASCADE,
        verbose_name=_('Система-клиент, поставившая на учет'),
    )
    liabilities_type = models.ForeignKey(
        'las.LiabilitiesType',
        on_delete=models.CASCADE,
        verbose_name=_('Идентификатор вида обязательств'),
    )
    receipt_number = models.CharField(
        db_index=True,
        max_length=100,
        verbose_name=_('Номер квитанции'),
    )
    amount_record = models.DecimalField(
        max_digits=17,
        decimal_places=2,
        verbose_name=_('Приращение количества согласно данной записи регистра'),
    )
    amount_total = models.DecimalField(
        max_digits=17,
        decimal_places=2,
        verbose_name=_('Суммарное количество по субъекту обязательств в разрезе вида обязательств'),
    )
    subject = models.ForeignKey(
        'las.SubjectAccumulation',
        on_delete=models.CASCADE,
        verbose_name=_('Идентификатор субъекта накопления'),
    )

    def __str__(self):
        return f'{self.receipt_number} ({self.id})'

    class Meta:
        verbose_name = _('Накопление в регистре накопления')
        verbose_name_plural = _('Накопления в регистре накопления')
