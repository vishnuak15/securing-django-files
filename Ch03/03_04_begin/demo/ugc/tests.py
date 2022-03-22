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
        cache.clear()

    def test_creates_object(self):
        self.assertEqual(Comment.objects.count(), 0)
        user_id = User.objects.first().id
        cache_key = '{}/comment_created'.format(user_id)

        self.assertFalse(cache.has_key(cache_key))
        create_comment(user_id, 'example')
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'example')
        self.assertEqual(cache.get(cache_key), comment.id)

    @patch('ugc.tasks.create_comment.retry')
    def test_retry(self, create_comment_retry):
        user_id = User.objects.first().id
        create_comment(user_id, 'example')
        create_comment_retry.side_effect = Retry()
        with self.assertRaises(Retry):
            create_comment(user_id, 'example')

class JournalTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='user', email='user@localhost'
        )
        self.auth_user = auth_header(create_access_token(self.user))

        self.other_user = User.objects.create(
            username='other_user', email='other_user@localhost'
        )
        self.auth_other_user = auth_header(create_access_token(self.other_user))
        Journal.objects.create(
            created_by=self.other_user, encrypted_text='hello-world'
        )

    def test_retrieve(self):
        journal = Journal.objects.create(
            created_by=self.user, encrypted_text='plaintext'
        )
        response = self.client.get(
            '/api/v1/journal/{}/'.format(journal.id),
            **self.auth_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': journal.id,
            'created_by': self.user.id,
            'encrypted_text': 'plaintext',
        })

    def test_list(self):
        journal = Journal.objects.create(
            created_by=self.user, encrypted_text='plaintext'
        )
        response = self.client.get('/api/v1/journal/', **self.auth_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{
                'id': journal.id,
                'created_by': self.user.id,
                'encrypted_text': 'plaintext',
            }]
        )

