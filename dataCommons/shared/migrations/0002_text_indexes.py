# -*- coding: utf-8 -*-

""" 002_text_indexes.py

    This manual South migration creates the Postgresql fulltext indexes used by
    the dataCommons.shared database.
"""
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        """ Apply this database migration.
        """
        # Add a full-text index to the Posting.heading field:

        db.execute("""
ALTER TABLE shared_posting
    ADD COLUMN heading_tsv tsvector;
CREATE TRIGGER tsvectorupdateheading BEFORE INSERT OR UPDATE ON shared_posting
    FOR EACH ROW
        EXECUTE PROCEDURE tsvector_update_trigger(heading_tsv,
                                                  'pg_catalog.english',
                                                  heading);
CREATE INDEX shared_posting_heading_tsv
    ON shared_posting USING gist(heading_tsv);
UPDATE shared_posting
    SET heading_tsv=to_tsvector(heading);""")

        # Add a full-text index to the Posting.body field:

        db.execute("""
ALTER TABLE shared_posting
    ADD COLUMN body_tsv tsvector;
CREATE TRIGGER tsvectorupdatebody BEFORE INSERT OR UPDATE ON shared_posting
    FOR EACH ROW
        EXECUTE PROCEDURE tsvector_update_trigger(body_tsv,
                                                  'pg_catalog.english',
                                                  body);
CREATE INDEX shared_posting_body_tsv
    ON shared_posting USING gist(body_tsv);
UPDATE shared_posting
    SET body_tsv=to_tsvector(body);""")


    def backwards(self, orm):
        """ Undo this database migration.
        """
        # Remove the full-text index on the Posting.heading field:

        db.execute("""
DROP TRIGGER tsvectorupdateheading on shared_posting;
DROP INDEX shared_posting_heading_tsv;
""")

        # Remove the full-text index on the Posting.body field:

        db.execute("""
DROP TRIGGER tsvectorupdatebody on shared_posting;
DROP INDEX shared_posting_body_tsv;
""")


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
