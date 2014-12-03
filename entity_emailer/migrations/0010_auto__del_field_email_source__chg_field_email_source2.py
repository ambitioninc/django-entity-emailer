# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Email.source'
        db.delete_column(u'entity_emailer_email', 'source_id')


        # Changing field 'Email.source2'
        db.alter_column(u'entity_emailer_email', 'source2_id', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['entity_event.Source']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Email.source'
        raise RuntimeError("Cannot reverse this migration. 'Email.source' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Email.source'
        db.add_column(u'entity_emailer_email', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_subscription.Source']),
                      keep_default=False)


        # Changing field 'Email.source2'
        db.alter_column(u'entity_emailer_email', 'source2_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_event.Source'], null=True))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'entity.entity': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'entity_kind'),)", 'object_name': 'Entity'},
            'display_name': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.IntegerField', [], {}),
            'entity_kind': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.EntityKind']", 'on_delete': 'models.PROTECT'}),
            'entity_meta': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'entity_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        u'entity.entitykind': {
            'Meta': {'object_name': 'EntityKind'},
            'display_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'db_index': 'True'})
        },
        u'entity_emailer.email': {
            'Meta': {'object_name': 'Email'},
            'context': ('jsonfield.fields.JSONField', [], {}),
            'from_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['entity.Entity']", 'symmetrical': 'False'}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'null': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'source2': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_event.Source']"}),
            'subentity_kind': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['entity.EntityKind']", 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_emailer.EmailTemplate']"}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True'})
        },
        u'entity_emailer.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'context_loader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'html_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'html_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'text_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'text_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'})
        },
        u'entity_event.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_event.SourceGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'entity_event.sourcegroup': {
            'Meta': {'object_name': 'SourceGroup'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['entity_emailer']