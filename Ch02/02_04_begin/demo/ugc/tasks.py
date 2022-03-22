from django.core.cache import cache
from django.contrib.auth.models import User

from demo.celery import app

@app.task(name='celery.ping')
def ping():
    pass
