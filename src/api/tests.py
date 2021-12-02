import json
import unittest

from django.urls import reverse
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    url_name = None

    @classmethod
    def setUpClass(cls):
        if cls is BaseAPITestCase:
            raise unittest.SkipTest('Abstract test case')

        super().setUpClass()

    def set_auth_jwt_token(self, username='test', password='test'):
        response = self.client.post(
            path=reverse('token_obtain_pair'),
            data=json.dumps({
                'username': username,
                'password': password,
            }),
            content_type='application/json'
        )
        token = response.json()['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'JWT {token}'

    def url(self, **kwargs):
        return reverse(self.url_name, **kwargs)

    def post(self, payload, **url_kwargs):
        return self.client.post(
            path=self.url(**url_kwargs),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def setUp(self):
        self.set_auth_jwt_token()

    def test_user_not_authenticated(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = None
        response = self.client.post(self.url())
        self.assertEqual(response.status_code, 401)

    def test_method_not_allowed(self):
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 405)

    def test_user_has_not_instance(self):
        self.user.instance = None
        self.user.save(update_fields=['instance'])
        response = self.client.post(self.url())
        self.assertEqual(response.status_code, 403)
