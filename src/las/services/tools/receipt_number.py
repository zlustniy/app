from typing import Optional

from django.utils.functional import cached_property
from django.utils.translation import gettext
from rest_framework.exceptions import ValidationError

from las.models import (
    Instance,
    LiabilitiesType,
    User,
    AccumulationRegister, SubjectAccumulation,
)
from las.services.tools.subject_accumulation import SubjectAccumulationManager, SubjectAccumulationEntity


class ReceiptNumberParseError(ValidationError):
    pass


class ReceiptNumberEntity:
    def __init__(self, receipt_number: str) -> None:
        """

        :type receipt_number: строка вида `0001-0005-00002` где:
        первый октет -  идентификатор инстанции las.models.Instance;
        второй октет -  идентификатор вида обязательств las.models.LiabilitiesType;
        третий октет -  идентификатор внутри группы инстанция+обязательства, который инкриминируется созданным sequence
                        receipt_number_seq_{instance.id}_{liability_type.id}.
        """
        self.number = receipt_number
        try:
            self.instance_id_octet, self.liability_type_id_octet, self.paid_id_octet = self.number.split(
                sep='-',
            )
            self.instance_id = int(self.instance_id_octet)
            self.liability_type_id = int(self.liability_type_id_octet)
            self.paid_id = int(self.paid_id_octet)
        except (AttributeError, ValueError):
            raise ReceiptNumberParseError(
                gettext('Невозможно декодировать receipt_number с значением=`{receipt_number}`').format(
                    receipt_number=self.number,
                ),
            )

    def __eq__(self, other):
        if not isinstance(other, ReceiptNumberEntity):
            return NotImplemented
        return self.number == other.number

    @cached_property
    def instance(self) -> Optional[Instance]:
        return Instance.objects.filter(id=self.instance_id).last()

    @cached_property
    def liability_type(self) -> LiabilitiesType | None:
        return LiabilitiesType.objects.filter(id=self.liability_type_id).last()

    @cached_property
    def accumulation_register(self) -> Optional[AccumulationRegister]:
        return AccumulationRegister.objects.filter(receipt_number=self.number).last()

    @cached_property
    def subject_accumulation(self) -> SubjectAccumulation:
        return self.accumulation_register.subject

    @cached_property
    def subject_accumulation_entity(self) -> SubjectAccumulationEntity:
        return SubjectAccumulationManager.transform(
            model_instance=self.subject_accumulation,
        )

    def is_instance_and_liability_type_instance_the_same(self):
        liability_type = self.liability_type
        return liability_type is not None and liability_type.instance == self.instance


class ReceiptNumberValidator:
    def __init__(self, receipt_number_entity: ReceiptNumberEntity) -> None:
        self.receipt_number_entity = receipt_number_entity

    def receipt_number_exists(self, raise_exception=False) -> bool:
        receipt_number_exists = self.receipt_number_entity.accumulation_register is not None
        if not receipt_number_exists and raise_exception:
            raise ValidationError(
                gettext('Записи в регистре с номером квитанции=`{receipt_number}` не существует').format(
                    receipt_number=self.receipt_number_entity.number,
                )
            )
        return receipt_number_exists

    def number_validate(self, user, raise_exception=False) -> bool:
        user_is_related_to_the_instance = user.instance == self.receipt_number_entity.instance
        liability_type_is_related_to_the_instance = self.receipt_number_entity.is_instance_and_liability_type_instance_the_same
        is_valid = all([
            user_is_related_to_the_instance,
            liability_type_is_related_to_the_instance,
        ])
        if not is_valid and raise_exception:
            if not user_is_related_to_the_instance:
                raise ValidationError(
                    gettext('Пользователь не может выполнять операции над квитанцией=`{receipt_number}`').format(
                        receipt_number=self.receipt_number_entity.number,
                    )
                )
            if not liability_type_is_related_to_the_instance:
                raise ValidationError(
                    gettext('Вид обязательства не доступен этой инстанции. Квитанция=`{receipt_number}`').format(
                        receipt_number=self.receipt_number_entity.number,
                    ),
                )
        return is_valid

    def valid(self, user: User, raise_exception=False) -> bool:
        return all([
            self.receipt_number_exists(raise_exception=raise_exception),
            self.number_validate(user=user, raise_exception=raise_exception)
        ])
