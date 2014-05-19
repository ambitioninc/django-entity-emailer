from datetime import datetime, timedelta

from entity.models import Entity
from django_dynamic_fixture import G
from django.test import TestCase
from mock import patch

from entity_emailer.models import Email, EmailType


class Test_handle_email_save(TestCase):
    def setUp(self):
        self.email_type = EmailType.objects.create(
            name='test_email',
            description='Do not actually send this. It is only for testing.'
        )
        self.send_to = G(Entity)

    @patch('entity_emailer.tasks.send_email_async_now')
    def test_calls_send_email_async_now(self, email_async_mock):
        Email.objects.create(
            email_type=self.email_type,
            send_to=self.send_to,
            subentity_type=None,
            subject='Test Email Please Ignore',
            template_path='path/to/template',
            context={'some': 'content'},
            uid=None,
            scheduled=None,
            sent=None,
        )
        self.assertTrue(email_async_mock.called)

    @patch('entity_emailer.tasks.send_email_async_now')
    def test_scheduled_emails_dont_call_async_email(self, email_async_mock):
        Email.objects.create(
            email_type=self.email_type,
            send_to=self.send_to,
            subentity_type=None,
            subject='Test Email Please Ignore',
            template_path='path/to/template',
            context={'some': 'content'},
            uid=None,
            scheduled=datetime.utcnow() + timedelta(days=100),
            sent=None,
        )
        self.assertFalse(email_async_mock.called)
