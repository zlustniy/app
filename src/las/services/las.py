import logging
from copy import deepcopy
from itertools import groupby
from typing import List

from django_redis import get_redis_connection
from redis_lock import Lock

from las.logger import LoggerMixin
from .register_add.handlers import RegisterAdd
from .register_cancel.handlers import RegisterCancel
from .register_edit.handlers import RegisterEdit
from .tools.receipt_number import ReceiptNumberEntity
from .tools.subject_accumulation import SubjectAccumulationEntity
from ..models import User


def get_lock(
        instance_id: int,
        subject_id: int | str,
        expire: int = 10,
        auto_renewal: bool = True,
) -> Lock:
    lock_conn = get_redis_connection('registration_accounting_events')
    lock_key = '{instance_id}_{subject_id}'.format(
        instance_id=instance_id,
        subject_id=subject_id,
    )

    return Lock(
        redis_client=lock_conn,
        name=lock_key,
        expire=expire,
        auto_renewal=auto_renewal,
    )


class LiabilityAccountingSystem(LoggerMixin):
    logger = logging.getLogger('las')

    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def get_groupby_payload(payload: List[dict]):
        payload = deepcopy(payload)
        for item in payload:
            item['receipt_number'] = ReceiptNumberEntity(receipt_number=item['receipt_number'])

        sorted_payload = sorted(payload, key=lambda x: x['receipt_number'].subject_accumulation.id)
        return groupby(sorted_payload, lambda x: x['receipt_number'].subject_accumulation_entity)

    def add(self, subject_accumulation: SubjectAccumulationEntity, payload: List[dict]) -> List[dict]:
        """

        :param subject_accumulation:
        :param payload: (RegisterAddInputLiabilitySerializer) = [
            {
               'accumulation_section_id': 1,
               'increment_amount': Decimal(1),
            },
                        {
               'accumulation_section_id': 2,
               'increment_amount': Decimal(2),
            },
        ]
        :return: [
            словарь вида: IncrementResult().asdict(),
            словарь вида: IncrementResult().asdict(),
        ]
        """
        with get_lock(
                instance_id=self.user.instance.id,
                subject_id=subject_accumulation.external_id,
        ):
            return RegisterAdd(
                user=self.user,
                subject_accumulation=subject_accumulation,
                payload=payload,
            ).add()

    def cancel(
            self,
            payload: List[dict],
    ) -> List[dict]:
        """

        :param payload: (RegisterCancelInputReceiptNumbersSerializer) = [
            {
               'receipt_number': '0001-0001-00554',
            },
            {
               'receipt_number': '0001-0001-00555',
            },,
        ]
        :return: [
            словарь вида: CancelResult().asdict(),
            словарь вида: CancelResult().asdict(),
        ]
        """
        for subject_accumulation, payload in LiabilityAccountingSystem.get_groupby_payload(
                payload=payload,
        ):
            with get_lock(
                    instance_id=self.user.instance.id,
                    subject_id=subject_accumulation.external_id,
            ):
                return RegisterCancel(
                    user=self.user,
                    payload=list(payload),
                ).cancel()

    def edit(
            self,
            payload: List[dict],
    ) -> List[dict]:
        """

        :param payload: (RegisterEditInputEditableLiabilitiesSerializer) = [
            {
               'new_amount': Decimal(1),
               'receipt_number': '0001-0002-03654',
            },
            {
               'new_amount': Decimal(2),
               'receipt_number': '0001-0001-03655',
            },,
        ]
        :return: [
            словарь вида: EditResult().asdict(),
            словарь вида: EditResult().asdict(),
        ]
        """
        for subject_accumulation, payload in LiabilityAccountingSystem.get_groupby_payload(
                payload=payload,
        ):
            with get_lock(
                    instance_id=self.user.instance.id,
                    subject_id=subject_accumulation.external_id,
            ):
                return RegisterEdit(
                    user=self.user,
                    payload=list(payload),
                ).edit()
