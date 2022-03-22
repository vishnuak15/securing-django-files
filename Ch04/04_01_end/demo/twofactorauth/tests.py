from django.contrib.auth.models import User
from django.test import TestCase

from api.models import ActivityLog
from api.utils import create_access_token, auth_header

from twofactorauth.models import TwoFactorAuthCode

class ValidateCodeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.auth_user = auth_header(create_access_token(self.user))

    def test_valid_code(self):
        pass

    def test_invalid_code(self):
        response = self.client.post(
            '/api/v1/validate',
            { 'auth_code': 'invalid' },
            **self.auth_user,
        )

