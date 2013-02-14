# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'LatLongSquare', fields ['int_latitude', 'int_longitude']
        db.delete_unique('geolocator_latlongsquare', ['int_latitude', 'int_longitude'])

        # Deleting model 'LatLongSquare'
        db.delete_table('geolocator_latlongsquare')

        # Deleting model 'PartialMatch'
        db.delete_table('geolocator_partialmatch')

        # Deleting model 'FullMatch'
        db.delete_table('geolocator_fullmatch')

        # Adding model 'LocationMatch'
        db.create_table('geolocator_locationmatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
            ('outline', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('geolocator', ['LocationMatch'])


    def backwards(self, orm):
        # Adding model 'LatLongSquare'
        db.create_table('geolocator_latlongsquare', (
            ('int_longitude', self.gf('django.db.models.fields.IntegerField')()),
            ('int_latitude', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('geolocator', ['LatLongSquare'])

        # Adding unique constraint on 'LatLongSquare', fields ['int_latitude', 'int_longitude']
        db.create_unique('geolocator_latlongsquare', ['int_latitude', 'int_longitude'])

        # Adding model 'PartialMatch'
        db.create_table('geolocator_partialmatch', (
            ('matching_part', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['PartialMatch'])

        # Adding model 'FullMatch'
        db.create_table('geolocator_fullmatch', (
            ('square', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geolocator.LatLongSquare'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Location'])),
        ))
        db.send_create_signal('geolocator', ['FullMatch'])

        # Deleting model 'LocationMatch'
        db.delete_table('geolocator_locationmatch')


    models = {
        'geolocator.locationmatch': {
            'Meta': {'object_name': 'LocationMatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Location']"}),
            'outline': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        'shared.location': {
            'Meta': {'object_name': 'Location'},
            'bounds_max_latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '5'}),
            'bounds_max_longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5'}),
            'bounds_min_latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '5'}),
            'bounds_min_longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['geolocator']