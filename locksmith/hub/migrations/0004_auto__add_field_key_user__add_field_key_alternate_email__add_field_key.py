# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Key.user'
        db.add_column('locksmith_hub_key', 'user',
                      self.gf('django.db.models.fields.related.OneToOneField')(related_name='api_key', unique=True, null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Key.alternate_email'
        db.add_column('locksmith_hub_key', 'alternate_email',
                      self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Key.promotable'
        db.add_column('locksmith_hub_key', 'promotable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Key.org_name'
        db.alter_column('locksmith_hub_key', 'org_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Key.name'
        db.alter_column('locksmith_hub_key', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Api.display_name'
        db.alter_column('locksmith_hub_api', 'display_name', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Api.documentation_link'
        db.alter_column('locksmith_hub_api', 'documentation_link', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting field 'Key.user'
        db.delete_column('locksmith_hub_key', 'user_id')

        # Deleting field 'Key.alternate_email'
        db.delete_column('locksmith_hub_key', 'alternate_email')

        # Deleting field 'Key.promotable'
        db.delete_column('locksmith_hub_key', 'promotable')


        # Changing field 'Key.org_name'
        db.alter_column('locksmith_hub_key', 'org_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Key.name'
        db.alter_column('locksmith_hub_key', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Api.display_name'
        db.alter_column('locksmith_hub_api', 'display_name', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Api.documentation_link'
        db.alter_column('locksmith_hub_api', 'documentation_link', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hub.api': {
            'Meta': {'object_name': 'Api', 'db_table': "'locksmith_hub_api'"},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'documentation_link': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'push_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signing_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'hub.key': {
            'Meta': {'object_name': 'Key', 'db_table': "'locksmith_hub_key'"},
            'alternate_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'org_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'org_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'promotable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'usage': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'api_key'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"})
        },
        'hub.keypublicationstatus': {
            'Meta': {'object_name': 'KeyPublicationStatus', 'db_table': "'locksmith_hub_keypublicationstatus'"},
            'api': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pub_statuses'", 'to': "orm['hub.Api']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pub_statuses'", 'to': "orm['hub.Key']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'hub.report': {
            'Meta': {'object_name': 'Report', 'db_table': "'locksmith_hub_report'"},
            'api': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['hub.Api']"}),
            'calls': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['hub.Key']"}),
            'reported_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['hub']