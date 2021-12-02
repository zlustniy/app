from collections import OrderedDict
from decimal import Decimal

from django.test import TestCase

from las.factories import LiabilitiesTypeFactory
from las.models import LiabilitiesType, AccumulationRegister
from las.models.liabilities_type import TypeRunningChoices
from las.services.register_add.handlers import RegisterAdd
from las.test_mixin import TestsMixin


class RegisterAddTestCase(TestsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.request_id = 1
        cls.liability_internal_accounting = LiabilitiesTypeFactory(
            instance=cls.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        cls.liability_external_accounting = LiabilitiesTypeFactory(
            instance=cls.instance,
            type_running=TypeRunningChoices.EXTERNAL.value[0],
        )

    def test_add(self):
        payload = [
            OrderedDict([
                ('accumulation_section_id', self.liability_internal_accounting.id),
                ('increment_amount', Decimal('1111.11')),
            ]),
            OrderedDict([
                ('accumulation_section_id', self.liability_external_accounting.id),
                ('increment_amount', Decimal('2222.22')),
            ]),
            OrderedDict([
                ('accumulation_section_id', LiabilitiesType.objects.last().id + 1),
                ('increment_amount', Decimal('3333.33')),
            ]),
            OrderedDict([
                ('accumulation_section_id', self.liability_internal_accounting.id),
                ('increment_amount', Decimal('4444.11')),
            ]),
        ]
        result = RegisterAdd(
            user=self.user,
            subject_accumulation=self.subject_accumulation,
            payload=payload,
        ).add()

        self.assertEqual(AccumulationRegister.objects.count(), 2)
        first_accumulation_register = AccumulationRegister.objects.filter(
            amount_record=payload[0]['increment_amount'],
            amount_total=payload[0]['increment_amount'],
            liabilities_type=self.liability_internal_accounting,
        ).first()
        self.assertIsNotNone(first_accumulation_register)
        self.assertIsNotNone(first_accumulation_register.receipt_number)
        second_accumulation_register = AccumulationRegister.objects.filter(
            amount_record=payload[3]['increment_amount'],
            amount_total=payload[3]['increment_amount'] + first_accumulation_register.amount_total,
            liabilities_type=self.liability_internal_accounting,
        ).first()
        self.assertIsNotNone(second_accumulation_register)
        self.assertIsNotNone(second_accumulation_register.receipt_number)

        self.assertListEqual(
            result,
            [
                {
                    'success': True,
                    'postfix': first_accumulation_register.liabilities_type.postfix,
                    'amount_record': first_accumulation_register.amount_record,
                    'amount_total': first_accumulation_register.amount_total,
                    'receipt_number': first_accumulation_register.receipt_number,
                },
                {
                    'success': False,
                    'postfix': None,
                    'amount_record': None,
                    'amount_total': None,
                    'receipt_number': None,
                },
                {
                    'success': False,
                    'postfix': None,
                    'amount_record': None,
                    'amount_total': None,
                    'receipt_number': None,
                },
                {
                    'success': True,
                    'postfix': second_accumulation_register.liabilities_type.postfix,
                    'amount_record': second_accumulation_register.amount_record,
                    'amount_total': second_accumulation_register.amount_total,
                    'receipt_number': second_accumulation_register.receipt_number,
                }
            ]
        )
