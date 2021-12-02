from collections import OrderedDict
from decimal import Decimal

import mock
from django.utils.translation import gettext

from api.tests import BaseAPITestCase
from las.factories import (
    LiabilitiesTypeFactory,
    UserFactory,
)
from las.models import AccumulationRegister
from las.models.liabilities_type import TypeRunningChoices
from las.test_mixin import TestsMixin


class RegisterEditAPIViewAPITestCase(TestsMixin, BaseAPITestCase):
    url_name = 'register_edit'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.liability_internal_accounting = LiabilitiesTypeFactory(
            instance=cls.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        cls.add_to_register(
            user=cls.user,
            liabilities_type=cls.liability_internal_accounting,
            subject_accumulation=cls.subject_accumulation,
            amounts=[Decimal('1000.00'), Decimal('2000.00'), Decimal('3500.00')],
        )

    def test_bad_request(self):
        response = self.client.post(
            self.url(),
            data={},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'payload': [gettext('Обязательное поле.')],
            }
        )

    def test_bad_request_receipt_numbers(self):
        response = self.post(
            payload={
                'payload': [],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'payload': {
                    'non_field_errors': [gettext('Этот список не может быть пустым.')],
                }
            }
        )

    def test_bad_request_negative_amount(self):
        last_accumulation_register = AccumulationRegister.objects.filter(
            user=self.user,
            liabilities_type=self.liability_internal_accounting,
        ).last()
        response = self.post(
            payload={
                'payload': [
                    {
                        'receipt_number': f'{last_accumulation_register.receipt_number}',
                        'new_amount': -22.22,
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'payload': [
                    {
                        'new_amount': ['Убедитесь, что это значение больше либо равно 0.']
                    },
                ],
            }
        )

    def test_bad_request_numbers_is_not_valid(self):
        other_user = UserFactory()
        other_liabilities_type = LiabilitiesTypeFactory(
            instance=other_user.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        self.add_to_register(
            user=other_user,
            liabilities_type=other_liabilities_type,
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('11000.00'), Decimal('12000.00'), Decimal('13500.00')],
        )
        last_accumulation_register = AccumulationRegister.objects.filter(
            user=self.user,
            liabilities_type=self.liability_internal_accounting,
        ).last()
        self.assertEqual(last_accumulation_register.amount_record, Decimal('3500.00'))
        self.assertEqual(last_accumulation_register.amount_total, Decimal('6500.00'))
        other_last_accumulation_register = AccumulationRegister.objects.filter(
            user=other_user,
            liabilities_type=other_liabilities_type,
        ).last()
        self.assertEqual(other_last_accumulation_register.amount_record, Decimal('13500.00'))
        self.assertEqual(other_last_accumulation_register.amount_total, Decimal('36500.00'))
        response = self.post(
            payload={
                'payload': [
                    {
                        'receipt_number': f'{other_last_accumulation_register.receipt_number}',
                        'new_amount': 12.22,
                    },
                    {
                        'receipt_number': f'{last_accumulation_register.receipt_number}',
                        'new_amount': 22.22,
                    },
                    {
                        'receipt_number': 'aaaa-bbbb-000nn',
                        'new_amount': 32.22,
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'payload': [
                    {'non_field_errors':
                        [
                            gettext(
                                'Пользователь не может выполнять операции над квитанцией=`{receipt_number}`').format(
                                receipt_number=other_last_accumulation_register.receipt_number,
                            )
                        ]
                    },
                    {},
                    {
                        'non_field_errors':
                            [
                                gettext('Невозможно декодировать receipt_number с значением=`{receipt_number}`').format(
                                    receipt_number='aaaa-bbbb-000nn',
                                )
                            ],
                    },
                ],
            }
        )

    @mock.patch('las.services.las.LiabilityAccountingSystem.edit')
    def test_success(self, mock_las_edit):
        other_user = UserFactory()
        other_liabilities_type = LiabilitiesTypeFactory(
            instance=other_user.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        self.add_to_register(
            user=other_user,
            liabilities_type=other_liabilities_type,
            subject_accumulation=self.subject_accumulation,
            amounts=[Decimal('11000.00'), Decimal('12000.00'), Decimal('13500.00')],
        )
        self.assertEqual(AccumulationRegister.objects.count(), 6)

        last_accumulation_register = AccumulationRegister.objects.filter(
            user=self.user,
            liabilities_type=self.liability_internal_accounting,
        ).last()
        self.assertEqual(last_accumulation_register.amount_record, Decimal('3500.00'))
        self.assertEqual(last_accumulation_register.amount_total, Decimal('6500.00'))
        other_last_accumulation_register = AccumulationRegister.objects.filter(
            user=other_user,
            liabilities_type=other_liabilities_type,
        ).last()
        self.assertEqual(other_last_accumulation_register.amount_record, Decimal('13500.00'))
        self.assertEqual(other_last_accumulation_register.amount_total, Decimal('36500.00'))
        mock_las_edit.return_value = [
            {
                'success': True,
                'postfix': '70361937514385032414102944330944',
                'amount_record': Decimal('22.22'),
                'amount_total': Decimal('3022.22'),
                'receipt_number': f'{last_accumulation_register.receipt_number}',
            }
        ]
        response = self.post(
            payload={
                'payload': [
                    {
                        'receipt_number': f'{last_accumulation_register.receipt_number}',
                        'new_amount': 22.22,
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_las_edit.assert_called_once_with(
            payload=[
                OrderedDict([
                    ('new_amount', Decimal('22.22')),
                    ('receipt_number', f'{last_accumulation_register.receipt_number}'),
                ]),
            ]
        )
        self.assertListEqual(
            response.json(),
            [
                {
                    'receipt_number': f'{last_accumulation_register.receipt_number}',
                    'postfix': '70361937514385032414102944330944',
                    'success': True,
                    'amount_total': 3022.22,
                    'amount_record': 22.22,
                },
            ]
        )
