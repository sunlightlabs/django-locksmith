# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Api.description'
        db.add_column('locksmith_hub_api', 'description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Api.status'
        db.add_column('locksmith_hub_api', 'status',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Api.mode'
        db.add_column('locksmith_hub_api', 'mode',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Api.display_name'
        db.add_column('locksmith_hub_api', 'display_name',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Api.documentation_link'
        db.add_column('locksmith_hub_api', 'documentation_link',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Api.description'
        db.delete_column('locksmith_hub_api', 'description')

        # Deleting field 'Api.status'
        db.delete_column('locksmith_hub_api', 'status')

        # Deleting field 'Api.mode'
        db.delete_column('locksmith_hub_api', 'mode')

        # Deleting field 'Api.display_name'
        db.delete_column('locksmith_hub_api', 'display_name')

        # Deleting field 'Api.documentation_link'
        db.delete_column('locksmith_hub_api', 'documentation_link')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hub.api': {
            'Meta': {'object_name': 'Api', 'db_table': "'locksmith_hub_api'"},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.TextField', [], {}),
            'documentation_link': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'push_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signing_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'hub.key': {
            'Meta': {'object_name': 'Key', 'db_table': "'locksmith_hub_key'"},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'org_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'org_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'usage': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'hub.keypublicationstatus': {
            'Meta': {'object_name': 'KeyPublicationStatus', 'db_table': "'locksmith_hub_keypublicationstatus'"},
            'api': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pub_statuses'", 'to': u"orm['hub.Api']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pub_statuses'", 'to': u"orm['hub.Key']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'hub.report': {
            'Meta': {'object_name': 'Report', 'db_table': "'locksmith_hub_report'"},
            'api': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': u"orm['hub.Api']"}),
            'calls': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': u"orm['hub.Key']"}),
            'reported_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['hub']