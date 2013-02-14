# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LatLongSquare'
        db.create_table('geolocator_latlongsquare', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('int_latitude', self.gf('django.db.models.fields.IntegerField')()),
            ('int_longitude', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('geolocator', ['LatLongSquare'])

        # Adding unique constraint on 'LatLongSquare', fields ['int_latitude', 'int_longitude']
        db.create_unique('geolocator_latlongsquare', ['int_latitude', 'int_longitude'])

        # Adding model 'FullMatches'
        db.create_table('geolocator_fullmatches', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['FullMatches'])

        # Adding model 'PartialMatches'
        db.create_table('geolocator_partialmatches', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
            ('matching_part', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('geolocator', ['PartialMatches'])


    def backwards(self, orm):
        # Removing unique constraint on 'LatLongSquare', fields ['int_latitude', 'int_longitude']
        db.delete_unique('geolocator_latlongsquare', ['int_latitude', 'int_longitude'])

        # Deleting model 'LatLongSquare'
        db.delete_table('geolocator_latlongsquare')

        # Deleting model 'FullMatches'
        db.delete_table('geolocator_fullmatches')

        # Deleting model 'PartialMatches'
        db.delete_table('geolocator_partialmatches')


    models = {
        'geolocator.fullmatches': {
            'Meta': {'object_name': 'FullMatches'},
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
        'geolocator.partialmatches': {
            'Meta': {'object_name': 'PartialMatches'},
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