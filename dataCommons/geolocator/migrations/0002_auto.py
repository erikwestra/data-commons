# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'FullMatches'
        db.delete_table('geolocator_fullmatches')

        # Deleting model 'PartialMatches'
        db.delete_table('geolocator_partialmatches')

        # Adding model 'PartialMatch'
        db.create_table('geolocator_partialmatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
            ('matching_part', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('geolocator', ['PartialMatch'])

        # Adding model 'FullMatch'
        db.create_table('geolocator_fullmatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['FullMatch'])


    def backwards(self, orm):
        # Adding model 'FullMatches'
        db.create_table('geolocator_fullmatches', (
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['FullMatches'])

        # Adding model 'PartialMatches'
        db.create_table('geolocator_partialmatches', (
            ('matching_part', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['PartialMatches'])

        # Deleting model 'PartialMatch'
        db.delete_table('geolocator_partialmatch')

        # Deleting model 'FullMatch'
        db.delete_table('geolocator_fullmatch')


    models = {
        'geolocator.fullmatch': {
            'Meta': {'object_name': 'FullMatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Location']"}),
            'square': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geolocator.LatLongSquare']"})
        },
        'geolocator.latlongsquare': {
            'Meta': {'unique_together': "(('int_latitude', 'int_longitude'),)", 'object_name': 'LatLongSquare'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_latitude': ('django.db.models.fields.IntegerField', [], {}),
            'int_longitude': ('django.db.models.fields.IntegerField', [], {})
        },
        'geolocator.partialmatch': {
            'Meta': {'object_name': 'PartialMatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Location']"}),
            'matching_part': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'square': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geolocator.LatLongSquare']"})
        },
        'shared.location': {
            'Meta': {'object_name': 'Location'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['geolocator']