from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.test import TestCase, SimpleTestCase
from django_dynamic_fixture import G, N
from entity.models import EntityKind

from entity_emailer.models import Email, EmailTemplate, IndividualEmail, GroupEmail


def basic_context_loader(context):
    return {'hello': 'hello'}


class EmailTemplateGetContextLoaderTest(SimpleTestCase):
    def test_loads_context_loader(self):
        template = EmailTemplate(context_loader='entity_emailer.tests.test_models.basic_context_loader')
        loader_func = template.get_context_loader_function()
        self.assertEqual(loader_func, basic_context_loader)

    def test_invalid_context_loader(self):
        template = EmailTemplate(context_loader='entity_emailer.tests.test_models.invalid_context_loader')
        with self.assertRaises(ImproperlyConfigured):
            template.get_context_loader_function()


class EmailTemplateCleanTest(SimpleTestCase):
    def test_validates(self):
        template = EmailTemplate(
            template_name='test',
            text_template_path='test/path'
        )
        template.clean()
        self.assertTrue(template)

    def test_invalid_context_path_does_not_validate(self):
        with self.assertRaises(ValidationError):
            EmailTemplate(
                template_name='test',
                text_template_path='test/path',
                context_loader='invalid_path',
            ).clean()

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


class EmailGetContext(SimpleTestCase):
    def test_without_context_loader(self):
        email = N(
            Email, context={'hi': 'hi'}, persist_dependencies=False, template=N(
                EmailTemplate, context_loader='entity_emailer.tests.test_models.basic_context_loader',
                persist_dependencies=False))
        self.assertEqual(email.get_context(), {'hello': 'hello'})

    def test_with_context_loader(self):
        email = N(Email, context={'hi': 'hi'}, persist_dependencies=False)
        self.assertEqual(email.get_context(), {'hi': 'hi'})


class IndividualEmailManagerTest(TestCase):
    def setUp(self):
        ek = G(EntityKind)
        temp = G(EmailTemplate, text_template='...')
        self.group_email = G(Email, template=temp, sub_entity_kind=ek, context={})
        self.individual_email = G(Email, template=temp, subentity_type=None, context={})

    def test_get_queryset_excludes_groups(self):
        qs = IndividualEmail.objects.get_queryset()
        self.assertNotIn(self.group_email.id, [e.id for e in qs])

    def test_get_queryset_includes_individuals(self):
        qs = IndividualEmail.objects.get_queryset()
        self.assertIn(self.individual_email.id, [e.id for e in qs])


class GroupEmailManagerTest(TestCase):
    def setUp(self):
        ek = G(EntityKind)
        temp = G(EmailTemplate, text_template='...')
        self.group_email = G(Email, template=temp, sub_entity_kind=ek, context={})
        self.individual_email = G(Email, template=temp, sub_entity_kind=None, context={})

    def test_get_queryset_excludes_individuals(self):
        qs = GroupEmail.objects.get_queryset()
        self.assertNotIn(self.individual_email.id, [e.id for e in qs])

    def test_get_queryset_includes_groups(self):
        qs = GroupEmail.objects.get_queryset()
        self.assertIn(self.group_email.id, [e.id for e in qs])
