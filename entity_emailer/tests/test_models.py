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

    def test_no_template_does_not_validate(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(template_name='empty').clean()

    def test_double_text_does_not_validate(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(
                template_name='double_text',
                text_template_path='test/path',
                text_template='test template',
            ).clean()

    def test_double_html_does_not_validate(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(
                template_name='double_html',
                html_template_path='test/path',
                html_template='test template',
            ).clean()


class EmailTemplateSaveTest(TestCase):
    def test_raises(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(template_name='empty').save()
