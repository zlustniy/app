

from decimal import Decimal
from typing import List

from las.factories import InstanceFactory
from las.models import User, LiabilitiesType
from las.models.liabilities_type import TypeRunningChoices
from las.services.las import LiabilityAccountingSystem
from las.services.tools.subject_accumulation import SubjectAccumulationEntity, SubjectAccumulationManager


class TestsMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user()
        cls.instance = InstanceFactory()
        cls.user.instance = cls.instance
        cls.user.save(update_fields=['instance'])
        cls.ogrn = '1023301286656'
        cls.name = 'ООО "Владимир-Тест"'
        cls.subject_accumulation = SubjectAccumulationManager.get_entity(
            external_id=cls.ogrn,
            external_description=cls.name,
        )

    @staticmethod
    def create_user(
            username='test',
            email='test@test.test',
            password='test',
    ) -> User:
        return User.objects.create_user(
            username,
            email,
            password,
        )

    @staticmethod
    def add_to_register(
            user: User,
            subject_accumulation: SubjectAccumulationEntity,
            liabilities_type: LiabilitiesType,
            amounts: List[Decimal],
            as_external=False,
    ) -> List[dict]:
        payload = []
        for amount in amounts:
            payload.append({
                'accumulation_section_id': liabilities_type.id,
                'increment_amount': amount,
            })
        if as_external:
            liabilities_type.type_running = TypeRunningChoices.INTERNAL.value[0]
            liabilities_type.save(update_fields=['type_running'])
        result = LiabilityAccountingSystem(
            user=user,
        ).add(
            subject_accumulation=subject_accumulation,
            payload=payload,
        )
        if as_external:
            liabilities_type.type_running = TypeRunningChoices.EXTERNAL.value[0]
            liabilities_type.save(update_fields=['type_running'])
        return result
