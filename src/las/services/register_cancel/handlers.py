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
from las.services.tools.subject_accumulation import SubjectAccumulationManager


@dataclass
class CancelResult:
    success: bool
    postfix: str = None
    amount_record: Decimal = None
    amount_total: Decimal = None
    receipt_number: str = None


class RegisterCancelBase(LoggerMixin):
    logger_name = 'register_cancel'

    def __init__(
            self,
            user: User,
    ):
        self.user = user


class RegisterCancelStrategyBase(RegisterCancelBase):
    log_prefix = 'RegisterCancelStrategy'

    def cancel(self, accumulation_register: AccumulationRegister) -> CancelResult:
        raise NotImplementedError


class RegisterCancelStrategyInsideLiabilitiesType(RegisterCancelStrategyBase):
    # Обработка `ВНУТРЕННЕГО` типа ведения учета

    def cancel(self, accumulation_register: AccumulationRegister) -> CancelResult:
        subject_accumulation = SubjectAccumulationManager.transform(
            model_instance=accumulation_register.subject,
        )
        last_total_amount = subject_accumulation.get_last_total_instance_amount(
            instance_id=self.user.instance.id,
            liabilities_type_id=accumulation_register.liabilities_type.id,
        )
        accumulation_register.pk = None
        accumulation_register.user = self.user
        accumulation_register.amount_record *= -1
        accumulation_register.amount_total = last_total_amount + accumulation_register.amount_record
        accumulation_register.save()
        cancel_result = CancelResult(
            success=True,
            receipt_number=accumulation_register.receipt_number,
            postfix=accumulation_register.liabilities_type.postfix,
            amount_record=accumulation_register.amount_record,
            amount_total=accumulation_register.amount_total,
        )
        return cancel_result


class RegisterCancelStrategyOutsideLiabilitiesType(RegisterCancelStrategyBase):
    # Обработка `ВНЕШНЕГО` типа ведения учета

    def cancel(self, accumulation_register: AccumulationRegister) -> CancelResult:
        cancel_result = CancelResult(
            success=False,
        )
        return cancel_result


class RegisterCancel(RegisterCancelBase):
    # Интерфейс снятия с учета обязательства
    log_prefix = 'RegisterCancel'

    def __init__(
            self,
            user: User,
            payload: List[dict],
    ):
        super().__init__(user=user)
        self.payload = payload

    @staticmethod
    def get_liability_type_strategy(liabilities_type: LiabilitiesType) -> Type[RegisterCancelStrategyBase]:
        liabilities_type_map = {
            TypeRunningChoices.INTERNAL.value[0]: RegisterCancelStrategyInsideLiabilitiesType,
            TypeRunningChoices.EXTERNAL.value[0]: RegisterCancelStrategyOutsideLiabilitiesType,
        }
        return liabilities_type_map.get(liabilities_type.type_running)

    def cancel(self) -> List[dict]:
        with transaction.atomic():
            results = []
            for receipt_number in self.payload:
                receipt_number_entity = receipt_number['receipt_number']
                accumulation_register = receipt_number_entity.accumulation_register
                strategy_class = self.get_liability_type_strategy(
                    liabilities_type=accumulation_register.liabilities_type,
                )
                self.log(
                    msg=f'receipt_number=`{receipt_number_entity.number}, '
                        f'accumulation_register=`{accumulation_register}` (id: `{accumulation_register.id}`), '
                        f'strategy_class=`{strategy_class}`. '
                        f'Init cancel.'
                )
                if strategy_class is not None:
                    results.append(strategy_class(
                        user=self.user,
                    ).cancel(
                        accumulation_register=accumulation_register,
                    ))

            results = list(map(asdict, results))
            self.log(msg=f'Cancelled: `{results}`')
            return results
