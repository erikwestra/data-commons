# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EventSource'
        db.create_table('monitoringAPI_eventsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal('monitoringAPI', ['EventSource'])

        # Adding model 'EventType'
        db.create_table('monitoringAPI_eventtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal('monitoringAPI', ['EventType'])

        # Adding model 'Event'
        db.create_table('monitoringAPI_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitoringAPI.EventSource'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitoringAPI.EventType'])),
            ('primary_value', self.gf('django.db.models.fields.IntegerField')()),
            ('secondary_value', self.gf('django.db.models.fields.IntegerField')()),
            ('posting_queue_total', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('monitoringAPI', ['Event'])


    def backwards(self, orm):
        # Deleting model 'EventSource'
        db.delete_table('monitoringAPI_eventsource')

        # Deleting model 'EventType'
        db.delete_table('monitoringAPI_eventtype')

        # Deleting model 'Event'
        db.delete_table('monitoringAPI_event')


    models = {
        'monitoringAPI.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting_queue_total': ('django.db.models.fields.IntegerField', [], {}),
            'primary_value': ('django.db.models.fields.IntegerField', [], {}),
            'secondary_value': ('django.db.models.fields.IntegerField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['monitoringAPI.EventSource']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['monitoringAPI.EventType']"})
        },
        'monitoringAPI.eventsource': {
            'Meta': {'object_name': 'EventSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        'monitoringAPI.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['monitoringAPI']