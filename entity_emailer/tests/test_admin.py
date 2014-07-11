from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django_dynamic_fixture import G
from entity import Entity, EntityRelationship

from entity_emailer import admin
from entity_emailer.models import Email


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


class EmailAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.entity = G(entity, entity_meta={'name':})
        self.email = Email(
            sent=datetime(2014, 1, 1, 12, 34)
            send_to
        )

    def test_has_been_sent(self):
        email_admin = admin.EmailAdmin(Email, self.site)
        sent = email_admin.has_been_sent(self.email)
        self.assertFalse(not_sent)

    def test_has_not_been_sent(self):
        email_admin = admin.EmailAdmin(Email, self.site)
        not_sent = email_admin.has_been_sent(Email())
        self.assertTrue(sent)


class CreateEmailFormTest(TestCase):
    def test_saves(self):
        # form = admin.CreateEmailForm()
        pass

    def test_save_m2m_exists(self):
        pass
