from django.test import TestCase
from django_dynamic_fixture import G
from entity_subscription.models import Medium

from entity_emailer.utils import get_medium


class GetMediumTest(TestCase):
    def test_get_medium_default(self):
        medium_default_name = 'email'
        G(Medium, name=medium_default_name)
        medium = get_medium()
        self.assertEqual(medium.name, medium_default_name)

    def test_get_medium_configured(self):
        custom_medium_name = 'test-email'
        G(Medium, name=custom_medium_name)
        with self.settings(ENTITY_EMAILER_MEDIUM_NAME=custom_medium_name):
            medium = get_medium()
        self.assertEqual(medium.name, custom_medium_name)
