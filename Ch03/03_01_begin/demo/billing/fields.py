from django.db.models import TextField
from cryptography.fernet import Fernet

from billing.utils import make_encryption_key

def encrypt(value):
    if value is None or value == '':
        return value

def decrypt(value):
    if value is None or value == '':
        return value

class EncryptedTextField(TextField):
    pass
