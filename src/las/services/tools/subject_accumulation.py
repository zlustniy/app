from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property

from las.models import (
    SubjectAccumulation,
    AccumulationRegister,
)


@dataclass
class SubjectAccumulationEntity:
    external_id: str
    external_description: str

    @cached_property
    def model_instance(self) -> SubjectAccumulation:
        subject_accumulation, _ = SubjectAccumulation.objects.get_or_create(
            ogrn=self.external_id,
            defaults={
                'name': self.external_description,
            },
        )
        return subject_accumulation

    def get_last_total_instance_amount(
            self,
            instance_id: int,
            liabilities_type_id: int,
    ) -> Decimal:
        accumulation_register = AccumulationRegister.objects.filter(
            user__instance_id=instance_id,
            subject_id=self.model_instance,
            liabilities_type_id=liabilities_type_id,
        ).last()
        if accumulation_register is not None:
            return accumulation_register.amount_total
        return Decimal('0')

    def log_representation(self):
        return 'external_id=`%s` (model_instance_id=`%s`)' % (
            self.external_id,
            self.model_instance.id,
        )


class SubjectAccumulationManager:
    @staticmethod
    def get_entity(external_id: str, external_description: str) -> SubjectAccumulationEntity:
        return SubjectAccumulationEntity(
            external_id=external_id,
            external_description=external_description,
        )

    @staticmethod
    def transform(model_instance: SubjectAccumulation) -> SubjectAccumulationEntity:
        return SubjectAccumulationManager.get_entity(
            external_id=model_instance.ogrn,
            external_description=model_instance.name,
        )
