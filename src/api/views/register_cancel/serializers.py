from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from las.logger import LoggerMixin
from las.services.tools.receipt_number import (
    ReceiptNumberValidator,
    ReceiptNumberEntity,
)


class RegisterCancelInputReceiptNumbersSerializer(LoggerMixin, serializers.Serializer):
    logger_name = 'register_cancel'

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    receipt_number = serializers.CharField(
        help_text=_('Номер "квитанции", выданной сервисом при регистрации заявки в данном виде обязательств'),
    )

    def validate(self, data):
        data = super().validate(data)
        ReceiptNumberValidator(
            receipt_number_entity=ReceiptNumberEntity(receipt_number=data['receipt_number']),
        ).valid(
            user=self.root.context['user'],
            raise_exception=True,
        )
        return data


class RegisterCancelInputSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    payload = serializers.ListSerializer(
        help_text=_('Массив с данными (по числу видов обязательств, в которых должна снята с учёта заявка)'),
        child=RegisterCancelInputReceiptNumbersSerializer(),
        allow_empty=False,
    )

    def validate(self, data):
        data = super().validate(data)
        data['payload'] = list(filter(lambda x: bool(x), data['payload']))
        return data


class RegisterCancelResponseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    receipt_number = serializers.CharField(
        max_length=100,
        help_text=_('Номер "квитанции" о регистрации заявки в данном виде обязательств'),
        allow_null=True,
    )
    postfix = serializers.CharField(
        max_length=32,
        help_text=_('Символьный идентификатор вида обязательств'),
        allow_null=True,
    )
    success = serializers.BooleanField(
        help_text=_('Признак успешности/ошибки операции снятия заявки с учёта в данном виде обязательств'),
    )
    amount_total = serializers.DecimalField(
        max_digits=17,
        decimal_places=2,
        help_text=_('суммарный размер обязательств данного клиента в данном виде обязательств, '
                    'сложившийся после снятия с учёта данной заявки'),
        allow_null=True,
    )
    amount_record = serializers.DecimalField(
        max_digits=17,
        decimal_places=2,
        help_text=_('Приращение суммарного размера обязательств данного клиента в данном виде обязательств, '
                    'вызванное отменой регистрации данной заявки'),
        allow_null=True,
    )
