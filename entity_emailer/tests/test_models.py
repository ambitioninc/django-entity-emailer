from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase, SimpleTestCase
from django_dynamic_fixture import G, N
from entity.models import EntityKind, Entity
from entity_event.models import Source
from freezegun import freeze_time

from entity_emailer.models import Email, EmailTemplate, IndividualEmail, GroupEmail
from entity_emailer.tests.utils import n_email, g_email


def basic_context_loader(context):
    return {'hello': 'hello'}


class EmailManagerCreateEmailTest(TestCase):
    @freeze_time('2013-2-3')
    def test_w_recipients_scheduled_time(self):
        source = G(Source)
        e1 = G(Entity)
        e2 = G(Entity)
        template = G(EmailTemplate, text_template_path='path')
        e = Email.objects.create_email(
            scheduled=datetime(2013, 4, 5), source=source, recipients=[e1, e2],
            subject='hi', from_address='hi@hi.com', template=template,
            context={'hi': 'hi'}, uid='hi')
        self.assertEqual(e.scheduled, datetime(2013, 4, 5))
        self.assertEqual(e.source, source)
        self.assertEqual(set(e.recipients.all()), set([e1, e2]))
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.template, template)
        self.assertEqual(e.context, {'hi': 'hi'})
        self.assertEqual(e.uid, 'hi')

    @freeze_time('2013-2-3')
    def test_w_recipients_no_scheduled_time(self):
        source = G(Source)
        e1 = G(Entity)
        e2 = G(Entity)
        template = G(EmailTemplate, text_template_path='path')
        e = Email.objects.create_email(
            source=source, recipients=[e1, e2],
            subject='hi', from_address='hi@hi.com', template=template,
            context={'hi': 'hi'}, uid='hi')
        self.assertEqual(e.scheduled, datetime(2013, 2, 3))
        self.assertEqual(e.source, source)
        self.assertEqual(set(e.recipients.all()), set([e1, e2]))
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.template, template)
        self.assertEqual(e.context, {'hi': 'hi'})
        self.assertEqual(e.uid, 'hi')

    @freeze_time('2013-2-3')
    def test_w_recipients_no_scheduled_time_no_recipients_no_uid(self):
        source = G(Source)
        template = G(EmailTemplate, text_template_path='path')
        e = Email.objects.create_email(
            source=source, subject='hi', from_address='hi@hi.com', template=template,
            context={'hi': 'hi'})
        self.assertEqual(e.scheduled, datetime(2013, 2, 3))
        self.assertEqual(e.source, source)
        self.assertEqual(list(e.recipients.all()), [])
        self.assertEqual(e.subject, 'hi')
        self.assertEqual(e.from_address, 'hi@hi.com')
        self.assertEqual(e.template, template)
        self.assertEqual(e.context, {'hi': 'hi'})
        self.assertIsNone(e.uid)


class EmailTemplateCleanTest(SimpleTestCase):
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


class EmailGetContext(SimpleTestCase):
    def test_without_context_loader(self):
        email = n_email(
            id=2, context={'hi': 'hi'}, view_uid='00001111222233334444555566667777', source=N(
                Source, context_loader='entity_emailer.tests.test_models.basic_context_loader',
                persist_dependencies=False))
        self.assertEqual(email.get_context(), {
            'hello': 'hello',
            'entity_emailer_id': '00001111222233334444555566667777',
        })

    def test_with_context_loader(self):
        email = n_email(id=3, context={'hi': 'hi'}, view_uid='00001111222233334444555566667777')
        self.assertEqual(email.get_context(), {
            'hi': 'hi',
            'entity_emailer_id': '00001111222233334444555566667777',
        })


class IndividualEmailManagerTest(TestCase):
    def setUp(self):
        ek = G(EntityKind)
        temp = G(EmailTemplate, text_template='...')
        self.group_email = g_email(template=temp, sub_entity_kind=ek, context={})
        self.individual_email = g_email(template=temp, subentity_type=None, context={})

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
        self.group_email = g_email(template=temp, sub_entity_kind=ek, context={})
        self.individual_email = g_email(template=temp, sub_entity_kind=None, context={})

    def test_get_queryset_excludes_individuals(self):
        qs = GroupEmail.objects.get_queryset()
        self.assertNotIn(self.individual_email.id, [e.id for e in qs])

    def test_get_queryset_includes_groups(self):
        qs = GroupEmail.objects.get_queryset()
        self.assertIn(self.group_email.id, [e.id for e in qs])
