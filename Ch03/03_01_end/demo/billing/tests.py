from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase

from billing.models import Payment

class PaymentTestCase(TestCase):
    def test_encryption(self):
        pass

