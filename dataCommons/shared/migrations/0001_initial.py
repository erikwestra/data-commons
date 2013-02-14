# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table('shared_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shared', ['Source'])

        # Adding model 'CategoryGroup'
        db.create_table('shared_categorygroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shared', ['CategoryGroup'])

        # Adding model 'Category'
        db.create_table('shared_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.CategoryGroup'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shared', ['Category'])

        # Adding model 'Location'
        db.create_table('shared_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12, db_index=True)),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shared', ['Location'])

        # Adding model 'Annotation'
        db.create_table('shared_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotation', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal('shared', ['Annotation'])

        # Adding model 'Posting'
        db.create_table('shared_posting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account_id', self.gf('django.db.models.fields.TextField')(null=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posting_source', to=orm['shared.Source'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posting_category', to=orm['shared.Category'])),
            ('category_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posting_cat_group', to=orm['shared.CategoryGroup'])),
            ('location_latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=5)),
            ('location_longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=5)),
            ('location_accuracy', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('location_country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_country', null=True, to=orm['shared.Location'])),
            ('location_state', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_state', null=True, to=orm['shared.Location'])),
            ('location_metro', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_metro', null=True, to=orm['shared.Location'])),
            ('location_region', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_region', null=True, to=orm['shared.Location'])),
            ('location_county', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_county', null=True, to=orm['shared.Location'])),
            ('location_city', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_city', null=True, to=orm['shared.Location'])),
            ('location_locality', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_locality', null=True, to=orm['shared.Location'])),
            ('location_zipcode', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='posting_zipcode', null=True, to=orm['shared.Location'])),
            ('external_id', self.gf('django.db.models.fields.TextField')()),
            ('external_url', self.gf('django.db.models.fields.TextField')(null=True)),
            ('heading', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')(null=True)),
            ('html', self.gf('django.db.models.fields.TextField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('language', self.gf('django.db.models.fields.TextField')(null=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('currency', self.gf('django.db.models.fields.TextField')(null=True)),
            ('status_offered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_lost', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_stolen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_found', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status_deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('immortal', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shared', ['Posting'])

        # Adding unique constraint on 'Posting', fields ['source', 'external_id']
        db.create_unique('shared_posting', ['source_id', 'external_id'])

        # Adding model 'PostingAnnotation'
        db.create_table('shared_postingannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('posting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Posting'])),
            ('annotation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Annotation'])),
        ))
        db.send_create_signal('shared', ['PostingAnnotation'])

        # Adding model 'ImageReference'
        db.create_table('shared_imagereference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('posting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Posting'])),
            ('full_url', self.gf('django.db.models.fields.TextField')(null=True)),
            ('thumbnail_url', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('shared', ['ImageReference'])


    def backwards(self, orm):
        # Removing unique constraint on 'Posting', fields ['source', 'external_id']
        db.delete_unique('shared_posting', ['source_id', 'external_id'])

        # Deleting model 'Source'
        db.delete_table('shared_source')

        # Deleting model 'CategoryGroup'
        db.delete_table('shared_categorygroup')

        # Deleting model 'Category'
        db.delete_table('shared_category')

        # Deleting model 'Location'
        db.delete_table('shared_location')

        # Deleting model 'Annotation'
        db.delete_table('shared_annotation')

        # Deleting model 'Posting'
        db.delete_table('shared_posting')

        # Deleting model 'PostingAnnotation'
        db.delete_table('shared_postingannotation')

        # Deleting model 'ImageReference'
        db.delete_table('shared_imagereference')


    models = {
        'shared.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'annotation': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'shared.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4', 'db_index': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.CategoryGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'shared.categorygroup': {
            'Meta': {'object_name': 'CategoryGroup'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'shared.imagereference': {
            'Meta': {'object_name': 'ImageReference'},
            'full_url': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Posting']"}),
            'thumbnail_url': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'shared.location': {
            'Meta': {'object_name': 'Location'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'shared.posting': {
            'Meta': {'unique_together': "(('source', 'external_id'),)", 'object_name': 'Posting'},
            'account_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posting_category'", 'to': "orm['shared.Category']"}),
            'category_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posting_cat_group'", 'to': "orm['shared.CategoryGroup']"}),
            'currency': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'external_id': ('django.db.models.fields.TextField', [], {}),
            'external_url': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'heading': ('django.db.models.fields.TextField', [], {}),
            'html': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immortal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'location_accuracy': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'location_city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_city'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_country'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_county': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_county'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '5'}),
            'location_locality': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_locality'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5'}),
            'location_metro': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_metro'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_region'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_state': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_state'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'location_zipcode': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'posting_zipcode'", 'null': 'True', 'to': "orm['shared.Location']"}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posting_source'", 'to': "orm['shared.Source']"}),
            'status_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'status_found': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_lost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_offered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_stolen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'shared.postingannotation': {
            'Meta': {'object_name': 'PostingAnnotation'},
            'annotation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Annotation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shared.Posting']"})
        },
        'shared.source': {
            'Meta': {'object_name': 'Source'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['shared']