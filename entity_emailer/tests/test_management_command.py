from django.core.management import call_command
from django.test import TestCase
from entity_subscription.models import Medium

from entity_emailer import get_medium

class AddEmailMediumCommandTest(TestCase):
    def test_idempotent(self):
        call_command('add_email_medium')
        call_command('add_email_medium')
        self.assertEqual(Medium.objects.count(), 1)

    def test_default(self):
        call_command('add_email_medium')
        medium = get_medium()
        self.assertEqual(medium.name, 'email')

    def test_custom(self):
        custom_medium_name='test-email'
        with self.settings(ENTITY_EMAILER_MEDIUM_NAME=custom_medium_name):
            call_command('add_email_medium')
            medium = get_medium()
        self.assertEqual(medium.name, custom_medium_name)

