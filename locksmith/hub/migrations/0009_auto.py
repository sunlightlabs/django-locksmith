# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Key', fields ['org_name']
        db.create_index('locksmith_hub_key', ['org_name'])

        # Adding index on 'Key', fields ['name']
        db.create_index('locksmith_hub_key', ['name'])

        # Adding index on 'Key', fields ['org_url']
        db.create_index('locksmith_hub_key', ['org_url'])

        # Adding index on 'Key', fields ['key']
        db.create_index('locksmith_hub_key', ['key'])


    def backwards(self, orm):
        # Removing index on 'Key', fields ['key']
        db.delete_index('locksmith_hub_key', ['key'])

        # Removing index on 'Key', fields ['org_url']
        db.delete_index('locksmith_hub_key', ['org_url'])

        # Removing index on 'Key', fields ['name']
        db.delete_index('locksmith_hub_key', ['name'])

        # Removing index on 'Key', fields ['org_name']
        db.delete_index('locksmith_hub_key', ['org_name'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hub.api': {
            'Meta': {'object_name': 'Api', 'db_table': "'locksmith_hub_api'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'documentation_link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'push_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'querybuilder_link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'signing_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'status_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tools_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'hub.key': {
            'Meta': {'object_name': 'Key', 'db_table': "'locksmith_hub_key'"},
            'alternate_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'org_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'org_url': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'promotable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'usage': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'api_key'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.User']"})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
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