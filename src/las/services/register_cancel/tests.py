from collections import OrderedDict
from decimal import Decimal

from django.test import TestCase

from las.factories import LiabilitiesTypeFactory
from las.models import AccumulationRegister
from las.models.liabilities_type import TypeRunningChoices
from las.services.register_cancel.handlers import RegisterCancel
from las.services.tools.receipt_number import ReceiptNumberEntity
from las.test_mixin import TestsMixin


class RegisterCancelTestCase(TestsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.liability_internal_accounting = LiabilitiesTypeFactory(
            instance=cls.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        cls.liability_external_accounting = LiabilitiesTypeFactory(
            instance=cls.instance,
            type_running=TypeRunningChoices.EXTERNAL.value[0],
        )

    def test_cancel(self):
        added_internal = self.add_to_register(
            user=self.user,
            liabilities_type=self.liability_internal_accounting,
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('1100.00'), Decimal('1200.00'), Decimal('1500.00')]
        )
        added_external = self.add_to_register(
            user=self.user,
            liabilities_type=self.liability_external_accounting,
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('11100.00'), Decimal('12200.00'), Decimal('13500.00')],
            as_external=True,
        )
        payload = [
            OrderedDict([('receipt_number', ReceiptNumberEntity(receipt_number=added_internal[1]['receipt_number']))]),
            OrderedDict([('receipt_number', ReceiptNumberEntity(receipt_number=added_external[1]['receipt_number']))]),
        ]
        self.assertEqual(AccumulationRegister.objects.count(), 6)
        result = RegisterCancel(
            user=self.user,
            payload=payload,
        ).cancel()
        self.assertEqual(AccumulationRegister.objects.count(), 7)
        canceled_accumulation_register = AccumulationRegister.objects.last()
        self.assertEqual(added_internal[1]['receipt_number'], canceled_accumulation_register.receipt_number)
        self.assertListEqual(
            result,
            [
                {
                    'success': True,
                    'postfix': f'{canceled_accumulation_register.liabilities_type.postfix}',
                    'amount_record': Decimal('-1200.00'),
                    'amount_total': Decimal('2600.00'),
                    'receipt_number': f'{canceled_accumulation_register.receipt_number}',
                },
                {
                    'success': False,
                    'postfix': None,
                    'amount_record': None,
                    'amount_total': None,
                    'receipt_number': None,
                },
            ]
        )
