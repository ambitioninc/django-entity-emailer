# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Email.template'
        db.delete_column(u'entity_emailer_email', 'template_id')

        # Deleting field 'Email.source'
        db.delete_column(u'entity_emailer_email', 'source_id')

        # Deleting field 'Email.context'
        db.delete_column(u'entity_emailer_email', 'context')
        
        # Deleting model 'EmailTemplate'
        db.delete_table(u'entity_emailer_emailtemplate')

        # Changing field 'Email.event'
        db.alter_column(u'entity_emailer_email', 'event_id', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['entity_event.Event']))

    def backwards(self, orm):
        # Adding model 'EmailTemplate'
        db.create_table(u'entity_emailer_emailtemplate', (
            ('text_template_path', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('template_name', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('html_template_path', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('text_template', self.gf('django.db.models.fields.TextField')(default='')),
            ('html_template', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'entity_emailer', ['EmailTemplate'])


        # User chose to not deal with backwards NULL issues for 'Email.template'
        raise RuntimeError("Cannot reverse this migration. 'Email.template' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Email.template'
        db.add_column(u'entity_emailer_email', 'template',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_emailer.EmailTemplate']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Email.source'
        raise RuntimeError("Cannot reverse this migration. 'Email.source' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Email.source'
        db.add_column(u'entity_emailer_email', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_event.Source']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Email.context'
        raise RuntimeError("Cannot reverse this migration. 'Email.context' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Email.context'
        db.add_column(u'entity_emailer_email', 'context',
                      self.gf('jsonfield.fields.JSONField')(),
                      keep_default=False)


        # Changing field 'Email.event'
        db.alter_column(u'entity_emailer_email', 'event_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_event.Event'], null=True))

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
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_event.Event']"}),
            'from_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['entity.Entity']", 'symmetrical': 'False'}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'null': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'sub_entity_kind': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['entity.EntityKind']", 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'view_uid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'entity_event.event': {
            'Meta': {'object_name': 'Event'},
            'context': ('jsonfield.fields.JSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_event.Source']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'time_expires': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(9999, 12, 31, 0, 0)', 'db_index': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'entity_event.source': {
            'Meta': {'object_name': 'Source'},
            'context_loader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
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
