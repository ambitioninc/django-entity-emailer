from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G
from entity import Entity, EntityRelationship
from entity_subscription.models import Source

from entity_emailer import admin
from entity_emailer.models import Email, EmailTemplate


class SubentityContentTypeQsTest(TestCase):
    def setUp(self):
        self.sub_entity_type_1 = G(ContentType)
        self.sub_entity_type_2 = G(ContentType)
        self.super_entity_type = G(ContentType)
        sub_entity_1 = G(Entity, entity_type=self.sub_entity_type_1)
        sub_entity_2 = G(Entity, entity_type=self.sub_entity_type_2)
        super_entity = G(Entity, entity_type=self.super_entity_type)
        G(EntityRelationship, sub_entity=sub_entity_1, super_entity=super_entity)
        G(EntityRelationship, sub_entity=sub_entity_2, super_entity=super_entity)

    def test_filters_non_subentity_types(self):
        qs = admin.get_subentity_content_type_qs()
        self.assertNotIn(self.super_entity_type, list(qs))

    def test_returns_subentity_types(self):
        qs = admin.get_subentity_content_type_qs()
        self.assertIn(self.sub_entity_type_1, list(qs))
        self.assertIn(self.sub_entity_type_2, list(qs))


class GetAllSuperEntitiesQsTest(TestCase):
    def setUp(self):
        self.super_entity_1 = G(Entity)
        self.sub_entity_1 = G(Entity)
        G(EntityRelationship, sub_entity=self.sub_entity_1, super_entity=self.super_entity_1)

    def test_filters_out_sub_entities(self):
        qs = admin.get_all_super_entities_qs()
        self.assertNotIn(self.sub_entity_1, list(qs))

    def test_includes_super_entities(self):
        qs = admin.get_all_super_entities_qs()
        self.assertIn(self.super_entity_1, list(qs))


class GetAllEmailableEntitiesTest(TestCase):
    def setUp(self):
        self.email_entity = G(Entity, entity_meta={'email': 'test@example.com'})
        self.no_email_entity = G(Entity, entity_meta={'name': 'Mr. T'})
        self.no_meta_entity = G(Entity)

    def test_filters_out_no_email(self):
        qs = admin.get_all_emailable_entities_qs()
        self.assertNotIn(self.no_email_entity, list(qs))

    def test_filters_out_no_meta(self):
        qs = admin.get_all_emailable_entities_qs()
        self.assertNotIn(self.no_meta_entity, list(qs))

    def test_includes_email_entities(self):
        qs = admin.get_all_emailable_entities_qs()
        self.assertIn(self.email_entity, list(qs))


class CreateGroupEmailFormTest(TestCase):
    def setUp(self):
        test_entity = G(Entity)
        test_entity_sub = G(Entity)
        G(EntityRelationship, sub_entity=test_entity_sub, super_entity=test_entity)
        G(Source, name='admin')
        G(EmailTemplate, template_name='html_safe', html_template='{{ html|safe }}')
        self.email_form_data = {
            'subject': 'A Test Email Subject',
            'from_email': 'test@example.com',
            'to_entity': test_entity.id,
            'body': '<html><body><p>This is the email body</p></body></html>',
        }

    def test_save_creates_email(self):
        form = admin.CreateGroupEmailForm(self.email_form_data)
        form.is_valid()
        form.save()
        self.assertTrue(Email.objects.exists())

    def test_save_m2m_exists(self):
        form = admin.CreateGroupEmailForm(self.email_form_data)
        form.save_m2m()


class GroupEmailAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.entity = G(Entity, entity_meta={'name': 'entity_name'})
        self.email = Email(
            sent=datetime(2014, 1, 1, 12, 34),
            send_to=self.entity,
        )

    def test_get_queryset_filters_non_admin(self):
        admin_template = G(EmailTemplate, template_name='html_safe', text_template="...")
        other_template = G(EmailTemplate, template_name='other', text_template="...")
        G(Email, template=admin_template, context={})
        G(Email, template=other_template, context={})
        email_admin = admin.GroupEmailAdmin(Email, self.site)
        qs = email_admin.get_queryset(None)
        self.assertEqual(qs.count(), 1)

    def test_has_been_sent(self):
        email_admin = admin.GroupEmailAdmin(Email, self.site)
        sent = email_admin.has_been_sent(self.email)
        self.assertTrue(sent)

    def test_has_not_been_sent(self):
        email_admin = admin.GroupEmailAdmin(Email, self.site)
        not_sent = email_admin.has_been_sent(Email())
        self.assertFalse(not_sent)

    def test_to(self):
        email_admin = admin.GroupEmailAdmin(Email, self.site)
        to = email_admin.to(self.email)
        self.assertEqual(to, 'entity_name')
