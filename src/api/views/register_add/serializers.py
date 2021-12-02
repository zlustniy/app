from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.fields import AmountField
from api.validators import is_digit


class RegisterAddInputLiabilitySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    accumulation_section_id = serializers.IntegerField(
        help_text=_('Идентификатор (в сервисе) вида обязательств'),
    )
    increment_amount = AmountField(
        help_text=_('Сумма (размер приращения обязательств)'),
    )


class RegisterAddInputSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    subject_ogrn = serializers.CharField(
        max_length=15,
        help_text=_('ОГРН (ОГРНИП) соискателя заявки (субъекта накопления)'),
        validators=[is_digit],
    )
    subject_name = serializers.CharField(
        help_text=_('Наименование соискателя заявки (субъекта накопления)'),
        allow_null=True,
        allow_blank=True,
        required=False,
    )
    request_id = serializers.IntegerField(
        help_text=_('Внутренний (в клиентской системе) идентификационный номер заявки'),
        required=False,
        allow_null=True,
    )
    payload = serializers.ListSerializer(
        help_text=_('Массив с данными (по числу видов обязательств, в которых должна быть учтена заявка)'),
        child=RegisterAddInputLiabilitySerializer(),
        allow_empty=False,
    )


class RegisterAddResponseSerializer(serializers.Serializer):
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
        help_text=_('Признак успешности/ошибки операции регистрации заявки в данном виде обязательств'),
    )
    amount_total = serializers.DecimalField(
        max_digits=17,
        decimal_places=2,
        help_text=_('Суммарный размер обязательств данного клиента в данном виде обязательств, '
                    'сложившийся после регистрации данной заявки'),
        allow_null=True,
    )
    amount_record = serializers.DecimalField(
        max_digits=17,
        decimal_places=2,
        help_text=_('Приращение суммарного размера обязательств данного клиента в данном виде обязательств, '
                    'вызванное регистрацией данной заявки'),
        allow_null=True,
    )


class RegisterAddResponseWrappedSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    request_id = serializers.IntegerField(
        help_text=_('Внутренний (в клиентской системе) идентификационный номер заявки'),
        allow_null=True,
    )
    payload = serializers.ListSerializer(
        help_text=_('Массив с данными (по числу видов обязательств, в которых требовалось зарегистрировать заявку)'),
        child=RegisterAddResponseSerializer(),
    )
