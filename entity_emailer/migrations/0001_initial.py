# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('entity', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table(u'entity_emailer_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_subscription.Source'])),
            ('send_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity.Entity'])),
            ('subentity_type', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['contenttypes.ContentType'], null=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('from_address', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entity_emailer.EmailTemplate'])),
            ('context', self.gf('jsonfield.fields.JSONField')()),
            ('uid', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, unique=True, null=True)),
            ('scheduled', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 7, 3, 0, 0), null=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal(u'entity_emailer', ['Email'])

        # Adding model 'EmailTemplate'
        db.create_table(u'entity_emailer_emailtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('text_template_path', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('html_template_path', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('text_template', self.gf('django.db.models.fields.TextField')(default='')),
            ('html_template', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'entity_emailer', ['EmailTemplate'])


    def backwards(self, orm):
        # Deleting model 'Email'
        db.delete_table(u'entity_emailer_email')

        # Deleting model 'EmailTemplate'
        db.delete_table(u'entity_emailer_emailtemplate')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'entity.entity': {
            'Meta': {'object_name': 'Entity'},
            'entity_id': ('django.db.models.fields.IntegerField', [], {}),
            'entity_meta': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'entity_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'entity_emailer.email': {
            'Meta': {'object_name': 'Email'},
            'context': ('jsonfield.fields.JSONField', [], {}),
            'from_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 7, 3, 0, 0)', 'null': 'True'}),
            'send_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.Entity']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_subscription.Source']"}),
            'subentity_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_emailer.EmailTemplate']"}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True'})
        },
        u'entity_emailer.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'html_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'html_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'text_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'text_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'})
        },
        u'entity_subscription.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['entity_emailer']
