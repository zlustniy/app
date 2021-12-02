from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import List, Type

from django.db import transaction

from las.logger import LoggerMixin
from las.models import (
    User,
    LiabilitiesType,
    AccumulationRegister,
)
from las.models.liabilities_type import TypeRunningChoices
from las.services.tools.subject_accumulation import SubjectAccumulationEntity


@dataclass
class IncrementResult:
    success: bool
    postfix: str = None
    amount_record: Decimal = None
    amount_total: Decimal = None
    receipt_number: str = None


class RegisterAddBase(LoggerMixin):
    logger_name = 'register_add'

    def __init__(
            self,
            user: User,
            subject_accumulation: SubjectAccumulationEntity,
    ):
        self.user = user
        self.subject_accumulation = subject_accumulation


class RegisterAddStrategyBase(RegisterAddBase):
    log_prefix = 'RegisterAddStrategy'

    def add(
            self,
            increment_amount: Decimal,
            liabilities_type: LiabilitiesType | None,
            forced_receipt_number: str | None = None
    ) -> IncrementResult:
        raise NotImplementedError


class RegisterAddStrategyInsideLiabilitiesType(RegisterAddStrategyBase):
    # Обработка `ВНУТРЕННЕГО` типа ведения учета

    def add(
            self,
            increment_amount: Decimal,
            liabilities_type: LiabilitiesType | None,
            forced_receipt_number: str | None = None
    ) -> IncrementResult:
        last_total_amount = self.subject_accumulation.get_last_total_instance_amount(
            instance_id=self.user.instance.id,
            liabilities_type_id=liabilities_type.id,
        )
        accumulation_register = AccumulationRegister.objects.create(
            user=self.user,
            liabilities_type=liabilities_type,
            subject=self.subject_accumulation.model_instance,
            amount_record=increment_amount,
            amount_total=last_total_amount + increment_amount,
            receipt_number=forced_receipt_number,
        )
        accumulation_register.refresh_from_db(fields=['receipt_number'])
        increment_result = IncrementResult(
            success=True,
            receipt_number=accumulation_register.receipt_number,
            postfix=accumulation_register.liabilities_type.postfix,
            amount_record=accumulation_register.amount_record,
            amount_total=accumulation_register.amount_total,
        )
        return increment_result


class RegisterAddStrategyOutsideLiabilitiesType(RegisterAddStrategyBase):
    # Обработка `ВНЕШНЕГО` типа ведения учета

    def add(
            self,
            increment_amount: Decimal,
            liabilities_type: LiabilitiesType | None,
            forced_receipt_number: str | None = None
    ) -> IncrementResult:
        increment_result = IncrementResult(
            success=False,
        )
        return increment_result


class RegisterAddStrategyUnknownLiabilitiesType(RegisterAddStrategyBase):
    # Обработка `НЕИЗВЕСТНОГО` типа ведения учета

    def add(
            self,
            increment_amount: Decimal,
            liabilities_type: LiabilitiesType | None,
            forced_receipt_number: str | None = None
    ):
        increment_result = IncrementResult(
            success=False,
        )
        return increment_result


class RegisterAdd(RegisterAddBase):
    # Интерфейс вызова постановки на учет обязательства в регистре накопления
    log_prefix = 'RegisterAdd'

    def __init__(
            self,
            user: User,
            subject_accumulation: SubjectAccumulationEntity,
            payload: List[dict],
    ):
        super().__init__(user=user, subject_accumulation=subject_accumulation)
        self.payload = payload

    @staticmethod
    def get_liability_type_strategy(
            liabilities_type: LiabilitiesType | None = None,
    ) -> Type[RegisterAddStrategyBase]:
        if liabilities_type is None:
            return RegisterAddStrategyUnknownLiabilitiesType

        liabilities_type_map = {
            TypeRunningChoices.INTERNAL.value[0]: RegisterAddStrategyInsideLiabilitiesType,
            TypeRunningChoices.EXTERNAL.value[0]: RegisterAddStrategyOutsideLiabilitiesType,
        }
        return liabilities_type_map.get(liabilities_type.type_running)

    def add(self, forced_receipt_number: str | None = None) -> List[dict]:
        with transaction.atomic():
            results = []
            for liability in self.payload:
                liabilities_type = LiabilitiesType.objects.filter(pk=liability['accumulation_section_id']).last()
                strategy_class = self.get_liability_type_strategy(liabilities_type=liabilities_type)

                self.log(
                    msg=f'liabilities_type.id=`{liabilities_type.id if liabilities_type else None}, '
                        f'liabilities_type.type_running=`{liabilities_type.type_running if liabilities_type else None}`, '
                        f'strategy_class=`{strategy_class}`.'
                        f'liability: `{liability}`. '
                        f'Init add.',
                )
                if strategy_class is not None:
                    results.append(strategy_class(
                        user=self.user,
                        subject_accumulation=self.subject_accumulation,
                    ).add(
                        increment_amount=liability['increment_amount'],
                        liabilities_type=liabilities_type,
                        forced_receipt_number=forced_receipt_number,
                    ))

            results = list(map(asdict, results))
            self.log(msg=f'Added: `{results}`')
            return results
