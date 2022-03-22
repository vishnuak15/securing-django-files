from django.db import models
from django.contrib.auth.models import User

from api.models import ActivityLog

class TwoFactorAuthCode(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=6)
    sent_on = models.DateTimeField(auto_now_add=True)

