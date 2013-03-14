# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Api'
        db.create_table('locksmith_hub_api', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('signing_key', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('push_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'hub', ['Api'])

        # Adding model 'Key'
        db.create_table('locksmith_hub_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('status', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('org_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('org_url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('usage', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('issued_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'hub', ['Key'])

        # Adding model 'KeyPublicationStatus'
        db.create_table('locksmith_hub_keypublicationstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pub_statuses', to=orm['hub.Key'])),
            ('api', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pub_statuses', to=orm['hub.Api'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'hub', ['KeyPublicationStatus'])

        # Adding model 'Report'
        db.create_table('locksmith_hub_report', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('api', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reports', to=orm['hub.Api'])),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reports', to=orm['hub.Key'])),
            ('endpoint', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('calls', self.gf('django.db.models.fields.IntegerField')()),
            ('reported_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'hub', ['Report'])


    def backwards(self, orm):
        # Deleting model 'Api'
        db.delete_table('locksmith_hub_api')

        # Deleting model 'Key'
        db.delete_table('locksmith_hub_key')

        # Deleting model 'KeyPublicationStatus'
        db.delete_table('locksmith_hub_keypublicationstatus')

        # Deleting model 'Report'
        db.delete_table('locksmith_hub_report')


    models = {
        u'hub.api': {
            'Meta': {'object_name': 'Api', 'db_table': "'locksmith_hub_api'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'push_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signing_key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
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
        }
    }

    complete_apps = ['hub']