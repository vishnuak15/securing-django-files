import base64
import re
from cryptography.fernet import Fernet

from unittest.mock import patch

from celery.exceptions import Retry
from celery.contrib.testing.worker import start_worker
import django.test
from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APISimpleTestCase

from demo.celery import app

from api.utils import create_access_token, auth_header
from api.models import ActivityLog
from ugc.models import Comment, Journal
from ugc.tasks import create_comment

class CreateCommentTaskTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_creates_object(self):
        self.assertEqual(Comment.objects.count(), 0)
        user_id = User.objects.first().id
        cache_key = '{}/comment_created'.format(user_id)
