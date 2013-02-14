# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Event.posting_queue_total'
        db.delete_column('monitoringAPI_event', 'posting_queue_total')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Event.posting_queue_total'
        raise RuntimeError("Cannot reverse this migration. 'Event.posting_queue_total' and its values cannot be restored.")

    models = {
        'monitoringAPI.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary_value': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'secondary_value': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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