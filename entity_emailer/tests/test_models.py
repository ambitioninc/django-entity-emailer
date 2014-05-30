from django.core.exceptions import ValidationError
from django.test import TestCase

from entity_emailer.models import EmailTemplate


class EmailTemplateCleanTest(TestCase):
    def test_validates(self):
        template = EmailTemplate(
            template_name='test',
            text_template_path='test/path'
        )
        template.clean()
        self.assertTrue(template)

    def test_does_not_validate(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(template_name='empty').clean()
