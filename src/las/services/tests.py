from collections import OrderedDict
from decimal import Decimal

import mock
from django.test import TestCase

from las.factories import LiabilitiesTypeFactory, SubjectAccumulationFactory
from las.models.liabilities_type import TypeRunningChoices
from las.services.las import LiabilityAccountingSystem
from las.services.tools.receipt_number import ReceiptNumberEntity
from las.services.tools.subject_accumulation import SubjectAccumulationManager
from las.test_mixin import TestsMixin


class LiabilityAccountingSystemTestCase(TestsMixin, TestCase):
    @mock.patch('las.services.register_add.handlers.RegisterAdd.add')
    @mock.patch('las.services.register_add.handlers.RegisterAdd.__init__')
    def test_call_add(self, mock_init, mock_add):
        mock_init.return_value = None
        liabilities = [
            OrderedDict([('accumulation_section_id', 1), ('increment_amount', Decimal('1111.11'))]),
            OrderedDict([('accumulation_section_id', 2), ('increment_amount', Decimal('2222.22'))]),
            OrderedDict([('accumulation_section_id', 3), ('increment_amount', Decimal('3333.33'))]),
        ]
        LiabilityAccountingSystem(
            user=self.user,
        ).add(
            subject_accumulation=self.subject_accumulation,
            payload=liabilities,
        )
        mock_init.assert_called_once_with(
            user=self.user,
            subject_accumulation=self.subject_accumulation,
            payload=liabilities,
        )
        mock_add.assert_called_once_with()

    def test_get_groupby_payload(self):
        subject_accumulation_1 = SubjectAccumulationManager.transform(model_instance=SubjectAccumulationFactory())
        subject_accumulation_2 = SubjectAccumulationManager.transform(model_instance=SubjectAccumulationFactory())
        subject_accumulation_3 = SubjectAccumulationManager.transform(model_instance=SubjectAccumulationFactory())
        liabilities_type = LiabilitiesTypeFactory(
            instance=self.user.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        added_user_1_1 = self.add_to_register(
            user=self.user,
            liabilities_type=liabilities_type,
            subject_accumulation=subject_accumulation_1,
            amounts=[Decimal('1000.00')]
        )
        added_user_2_1 = self.add_to_register(
            user=self.user,
            liabilities_type=liabilities_type,
            subject_accumulation=subject_accumulation_2,
            amounts=[Decimal('1000.00')]
        )
        added_user_1_2 = self.add_to_register(
            user=self.user,
            liabilities_type=liabilities_type,
            subject_accumulation=subject_accumulation_1,
            amounts=[Decimal('1000.00')]
        )
        added_user_3_1 = self.add_to_register(
            user=self.user,
            liabilities_type=liabilities_type,
            subject_accumulation=subject_accumulation_3,
            amounts=[Decimal('1000.00')]
        )
        added_user_2_2 = self.add_to_register(
            user=self.user,
            liabilities_type=liabilities_type,
            subject_accumulation=subject_accumulation_2,
            amounts=[Decimal('1000.00')]
        )
        receipt_numbers = [
            OrderedDict([('receipt_number', added_user_1_1[0]['receipt_number'])]),
            OrderedDict([('receipt_number', added_user_2_1[0]['receipt_number'])]),
            OrderedDict([('receipt_number', added_user_1_2[0]['receipt_number'])]),
            OrderedDict([('receipt_number', added_user_3_1[0]['receipt_number'])]),
            OrderedDict([('receipt_number', added_user_2_2[0]['receipt_number'])]),
        ]
        excepted_receipt_numbers = [
            (
                subject_accumulation_1,
                [
                    added_user_1_1[0]['receipt_number'],
                    added_user_1_2[0]['receipt_number'],
                ]
            ),
            (
                subject_accumulation_2,
                [
                    added_user_2_1[0]['receipt_number'],
                    added_user_2_2[0]['receipt_number'],
                ]
            ),
            (
                subject_accumulation_3,
                [
                    added_user_3_1[0]['receipt_number'],
                ]
            ),
        ]
        for index, value in enumerate(LiabilityAccountingSystem.get_groupby_payload(
                payload=receipt_numbers,
        )):
            subject, numbers = value
            excepted_subject, excepted_numbers = excepted_receipt_numbers[index]
            self.assertEqual(subject, excepted_subject)
            self.assertListEqual(
                [x['receipt_number'].number for x in numbers],
                excepted_numbers,
            )

    @mock.patch('las.services.register_cancel.handlers.RegisterCancel.cancel')
    @mock.patch('las.services.register_cancel.handlers.RegisterCancel.__init__')
    def test_call_cancel(self, mock_init, mock_cancel):
        mock_init.return_value = None
        added = self.add_to_register(
            user=self.user,
            liabilities_type=LiabilitiesTypeFactory(
                instance=self.user.instance,
                type_running=TypeRunningChoices.INTERNAL.value[0],
            ),
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('1000.00')]
        )
        receipt_numbers = [
            OrderedDict([('receipt_number', added[0]['receipt_number'])]),
        ]
        LiabilityAccountingSystem(
            user=self.user,
        ).cancel(
            payload=receipt_numbers,
        )

        mock_init.assert_called_once_with(
            user=self.user,
            payload=[
                OrderedDict([
                    ('receipt_number', ReceiptNumberEntity(receipt_numbers[0]['receipt_number'])),
                ]),
            ],
        )
        mock_cancel.assert_called_once_with()

    @mock.patch('las.services.register_edit.handlers.RegisterEdit.edit')
    @mock.patch('las.services.register_edit.handlers.RegisterEdit.__init__')
    def test_call_edit(self, mock_init, mock_edit):
        mock_init.return_value = None
        added = self.add_to_register(
            user=self.user,
            liabilities_type=LiabilitiesTypeFactory(
                instance=self.user.instance,
                type_running=TypeRunningChoices.INTERNAL.value[0],
            ),
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('1000.00')]
        )
        editable_liabilities = [
            OrderedDict([
                ('receipt_number', added[0]['receipt_number']),
                ('new_amount', Decimal(22.22)),
            ]),
        ]
        LiabilityAccountingSystem(
            user=self.user,
        ).edit(
            payload=editable_liabilities,
        )
        mock_init.assert_called_once_with(
            user=self.user,
            payload=[
                OrderedDict([
                    ('receipt_number', ReceiptNumberEntity(added[0]['receipt_number'])),
                    ('new_amount', Decimal(22.22)),
                ]),
            ],
        )
        mock_edit.assert_called_once_with()
