from collections import OrderedDict
from decimal import Decimal

from django.test import TestCase

from las.factories import LiabilitiesTypeFactory
from las.models import AccumulationRegister
from las.models.liabilities_type import TypeRunningChoices
from las.services.register_edit.handlers import RegisterEdit
from las.services.tools.receipt_number import ReceiptNumberEntity
from las.test_mixin import TestsMixin


class RegisterEditTestCase(TestsMixin, TestCase):
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

    def test_edit(self):
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
        editable_liabilities = [
            OrderedDict([
                ('receipt_number', ReceiptNumberEntity(receipt_number=added_internal[1]['receipt_number'])),
                ('new_amount', Decimal('22.22')),
            ]),
            OrderedDict([
                ('receipt_number', ReceiptNumberEntity(receipt_number=added_external[1]['receipt_number'])),
                ('new_amount', Decimal('33.33')),
            ]),
        ]
        self.assertEqual(
            AccumulationRegister.objects.filter(
                receipt_number=added_internal[1]['receipt_number'],
            ).count(),
            1,
        )
        result = RegisterEdit(
            user=self.user,
            payload=editable_liabilities,
        ).edit()
        self.assertEqual(
            AccumulationRegister.objects.filter(
                receipt_number=added_internal[1]['receipt_number'],
            ).count(),
            3,
        )
        added, canceled, edited = AccumulationRegister.objects.filter(
            receipt_number=added_internal[1]['receipt_number'],
        ).order_by('id')
        self.assertEqual(added.amount_record, Decimal('1200.00'))
        self.assertEqual(added.amount_total, Decimal('2300.00'))
        self.assertEqual(canceled.amount_record, -Decimal('1200.00'))
        self.assertEqual(canceled.amount_total, Decimal('2600.00'))
        self.assertEqual(edited.amount_record, Decimal('22.22'))
        self.assertEqual(edited.amount_total, Decimal('2622.22'))
        self.assertListEqual(
            result,
            [
                {
                    'success': True,
                    'postfix': edited.liabilities_type.postfix,
                    'amount_record': edited.amount_record,
                    'amount_total': edited.amount_total,
                    'receipt_number': edited.receipt_number,
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
