from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_dynamic_fixture import G

from entity_emailer.models import Email, EmailTemplate, IndividualEmail, GroupEmail


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


class EmailTemplateUnicodeTest(TestCase):
    def test_returns_name(self):
        name = 'test-name'
        template = G(EmailTemplate, template_name=name, text_template='...')
        self.assertEqual(template.__unicode__(), name)


class IndividualEmailManagerTest(TestCase):
    def setUp(self):
        ct = G(ContentType)
        temp = G(EmailTemplate, text_template='...')
        self.group_email = G(Email, template=temp, subentity_type=ct, context={})
        self.individual_email = G(Email, template=temp, subentity_type=None, context={})

    def test_get_queryset_excludes_groups(self):
        qs = IndividualEmail.objects.get_queryset()
        self.assertNotIn(self.group_email.id, [e.id for e in qs])

    def test_get_queryset_includes_individuals(self):
        qs = IndividualEmail.objects.get_queryset()
        self.assertIn(self.individual_email.id, [e.id for e in qs])


class GroupEmailManagerTest(TestCase):
    def setUp(self):
        ct = G(ContentType)
        temp = G(EmailTemplate, text_template='...')
        self.group_email = G(Email, template=temp, subentity_type=ct, context={})
        self.individual_email = G(Email, template=temp, subentity_type=None, context={})

    def test_get_queryset_excludes_individuals(self):
        qs = GroupEmail.objects.get_queryset()
        self.assertNotIn(self.individual_email.id, [e.id for e in qs])

    def test_get_queryset_includes_groups(self):
        qs = GroupEmail.objects.get_queryset()
        print qs.values()
        print self.group_email.__dict__
        self.assertIn(self.group_email.id, [e.id for e in qs])
