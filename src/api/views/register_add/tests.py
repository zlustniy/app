from collections import OrderedDict
from decimal import Decimal

import mock
from django.utils.translation import gettext

from api.tests import BaseAPITestCase
from las.factories import LiabilitiesTypeFactory
from las.models import AccumulationRegister
from las.models.liabilities_type import TypeRunningChoices
from las.test_mixin import TestsMixin


class RegisterAddAPIViewAPITestCase(TestsMixin, BaseAPITestCase):
    url_name = 'register_add'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.request_id = 1

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
                'subject_ogrn': [gettext('Обязательное поле.')],
                'payload': [gettext('Обязательное поле.')],
            }
        )

    def test_bad_request_negative_amount(self):
        response = self.post(
            payload={
                'subject_ogrn': self.ogrn,
                'subject_name': self.name,
                'request_id': self.request_id,
                'payload': [
                    {
                        'accumulation_section_id': 1,
                        'increment_amount': '1111.11'
                    },
                    {
                        'accumulation_section_id': 2,
                        'increment_amount': '-2222.22'
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'payload': [
                    {},
                    {
                        'increment_amount': ['Убедитесь, что это значение больше либо равно 0.']
                    },
                ],
            }
        )

    def test_bad_request_liabilities(self):
        response = self.post(
            payload={
                'subject_ogrn': self.ogrn,
                'subject_name': '',
                'request_id': self.request_id,
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

    @mock.patch('las.services.las.LiabilityAccountingSystem.add')
    @mock.patch('las.services.las.LiabilityAccountingSystem.__init__')
    def test_success(self, mock_init, mock_las_add):
        mock_init.return_value = None
        mock_las_add.return_value = [
            {
                'receipt_number': '0001-0001-00724',
                'postfix': '7',
                'success': True,
                'amount_total': 1111.11,
                'amount_record': 1111.11
            },
            {
                'receipt_number': None,
                'postfix': None,
                'success': False,
                'amount_total': None,
                'amount_record': None
            }
        ]
        response = self.post(
            payload={
                'subject_ogrn': self.ogrn,
                'subject_name': self.name,
                'request_id': self.request_id,
                'payload': [
                    {
                        'accumulation_section_id': 1,
                        'increment_amount': '1111.11'
                    },
                    {
                        'accumulation_section_id': 2,
                        'increment_amount': '2222.22'
                    },
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        mock_init.assert_called_once_with(
            user=self.user,
        )
        mock_las_add.assert_called_once_with(
            subject_accumulation=self.subject_accumulation,
            payload=[
                OrderedDict([('accumulation_section_id', 1), ('increment_amount', Decimal('1111.11'))]),
                OrderedDict([('accumulation_section_id', 2), ('increment_amount', Decimal('2222.22'))]),
            ]
        )
        self.assertDictEqual(
            response.json(),
            {
                'request_id': self.request_id,
                'payload': [
                    {
                        'receipt_number': '0001-0001-00724',
                        'postfix': '7',
                        'success': True,
                        'amount_total': 1111.11,
                        'amount_record': 1111.11,
                    },
                    {
                        'receipt_number': None,
                        'postfix': None,
                        'success': False,
                        'amount_total': None,
                        'amount_record': None,
                    },
                ],
            }
        )

    def test_all_success_without_subject_name_and_request(self):
        liability_internal_accounting = LiabilitiesTypeFactory(
            instance=self.instance,
            type_running=TypeRunningChoices.INTERNAL.value[0],
        )
        self.assertEqual(AccumulationRegister.objects.count(), 0)
        response = self.post(
            payload={
                'subject_ogrn': self.ogrn,
                'payload': [
                    {
                        'accumulation_section_id': liability_internal_accounting.id,
                        'increment_amount': '1111.11'
                    },
                ],
            },
        )
        self.assertEqual(AccumulationRegister.objects.count(), 1)
        accumulation_register = AccumulationRegister.objects.last()
        self.assertIsNone(accumulation_register.subject.name)
        self.assertDictEqual(
            response.json(),
            {
                'request_id': None,
                'payload': [
                    {
                        'receipt_number': accumulation_register.receipt_number,
                        'postfix': accumulation_register.liabilities_type.postfix,
                        'success': True,
                        'amount_total': float(accumulation_register.amount_total),
                        'amount_record': float(accumulation_register.amount_record),
                    },
                ],
            }
        )
