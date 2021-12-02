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
from las.services.register_add.handlers import RegisterAddStrategyInsideLiabilitiesType
from las.services.register_cancel.handlers import RegisterCancelStrategyInsideLiabilitiesType
from las.services.tools.subject_accumulation import SubjectAccumulationManager


@dataclass
class EditResult:
    success: bool
    postfix: str = None
    amount_record: Decimal = None
    amount_total: Decimal = None
    receipt_number: str = None


class RegisterEditBase(LoggerMixin):
    logger_name = 'register_edit'

    def __init__(
            self,
            user: User,
    ):
        self.user = user


class RegisterEditStrategyBase(RegisterEditBase):
    log_prefix = 'RegisterEditStrategy'

    def edit(self, accumulation_register: AccumulationRegister, editable_liability: dict) -> EditResult:
        raise NotImplementedError


class RegisterEditStrategyInsideLiabilitiesType(RegisterEditStrategyBase):
    # Обработка `ВНУТРЕННЕГО` типа ведения учета

    def edit(self, accumulation_register: AccumulationRegister, editable_liability: dict) -> EditResult:
        RegisterCancelStrategyInsideLiabilitiesType(
            user=self.user,
        ).cancel(
            accumulation_register=accumulation_register,
        )
        register_add_result = RegisterAddStrategyInsideLiabilitiesType(
            user=self.user,
            subject_accumulation=SubjectAccumulationManager.transform(
                model_instance=accumulation_register.subject,
            ),
        ).add(
            increment_amount=editable_liability['new_amount'],
            liabilities_type=accumulation_register.liabilities_type,
            forced_receipt_number=accumulation_register.receipt_number,
        )

        edit_result = EditResult(
            success=True,
            receipt_number=register_add_result.receipt_number,
            postfix=register_add_result.postfix,
            amount_record=register_add_result.amount_record,
            amount_total=register_add_result.amount_total,
        )
        return edit_result


class RegisterEditStrategyOutsideLiabilitiesType(RegisterEditStrategyBase):
    # Обработка `ВНЕШНЕГО` типа ведения учета

    def edit(self, accumulation_register: AccumulationRegister, editable_liability: dict) -> EditResult:
        edit_result = EditResult(
            success=False,
        )
        return edit_result


class RegisterEdit(RegisterEditBase):
    # Интерфейс изменения обязательства
    log_prefix = 'RegisterEdit'

    def __init__(
            self,
            user: User,
            payload: List[dict],
    ):
        super().__init__(user=user)
        self.payload = payload

    @staticmethod
    def get_liability_type_strategy(liabilities_type: LiabilitiesType) -> Type[RegisterEditStrategyBase]:
        liabilities_type_map = {
            TypeRunningChoices.INTERNAL.value[0]: RegisterEditStrategyInsideLiabilitiesType,
            TypeRunningChoices.EXTERNAL.value[0]: RegisterEditStrategyOutsideLiabilitiesType,
        }
        return liabilities_type_map.get(liabilities_type.type_running)

    def edit(self) -> List[dict]:
        with transaction.atomic():
            results = []
            for editable_liability in self.payload:
                receipt_number_entity = editable_liability['receipt_number']
                accumulation_register = receipt_number_entity.accumulation_register
                strategy_class = self.get_liability_type_strategy(
                    liabilities_type=accumulation_register.liabilities_type,
                )
                self.log(
                    msg=f'receipt_number=`{receipt_number_entity.number}, '
                        f'accumulation_register=`{accumulation_register}` (id: `{accumulation_register.id}`), '
                        f'strategy_class=`{strategy_class}`. '
                        f'Init edit.'
                )
                if strategy_class is not None:
                    results.append(strategy_class(
                        user=self.user,
                    ).edit(
                        accumulation_register=accumulation_register,
                        editable_liability=editable_liability,
                    ))

            results = list(map(asdict, results))
            self.log(msg=f'Edited: `{results}`')
            return results
