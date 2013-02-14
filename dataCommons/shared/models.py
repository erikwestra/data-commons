""" dataCommons.shared.models

    This file contains the Django models used by the "shared" application.
"""
import datetime

from django.db import models
from django.db import connection

#############################################################################

class Source(models.Model):
    """ A source of posting data.
    """
    id   = models.AutoField(primary_key=True)
    code = models.CharField(max_length=8, db_index=True, unique=True)
    name = models.CharField(max_length=255)

#############################################################################

class CategoryGroup(models.Model):
    """ A top-level grouping of categories.
    """
    id   = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4, db_index=True, unique=True)
    name = models.CharField(max_length=255)

#############################################################################

class Category(models.Model):
    """ A posting category.
    """
    id    = models.AutoField(primary_key=True)
    group = models.ForeignKey(CategoryGroup)
    rank  = models.IntegerField(db_index=True)
    code  = models.CharField(max_length=4, db_index=True, unique=True)
    name  = models.CharField(max_length=255)

#############################################################################

class Location(models.Model):
    """ A location.

        Note that this is a simple flat table of all known locations.
        Eventually, we will add more fields to support parent/child
        relationships.
    """
    LEVEL_COUNTRY  = 1
    LEVEL_STATE    = 2
    LEVEL_METRO    = 3
    LEVEL_REGION   = 4
    LEVEL_COUNTY   = 5
    LEVEL_CITY     = 6
    LEVEL_LOCALITY = 7
    LEVEL_ZIPCODE  = 8

    LEVEL_CHOICES = ((LEVEL_COUNTRY,  "country"),
                     (LEVEL_STATE,    "state"),
                     (LEVEL_METRO,    "metro"),
                     (LEVEL_REGION,   "region"),
                     (LEVEL_COUNTY,   "county"),
                     (LEVEL_CITY,     "city"),
                     (LEVEL_LOCALITY, "locality"),
                     (LEVEL_ZIPCODE,  "zipcode"))

    id                   = models.AutoField(primary_key=True)
    code                 = models.CharField(max_length=12, db_index=True,
                                            unique=True)
    level                = models.IntegerField(choices=LEVEL_CHOICES)
    short_name           = models.CharField(max_length=255)
    full_name            = models.CharField(max_length=255)
    bounds_min_latitude  = models.DecimalField(max_digits=7, decimal_places=5,
                                               null=True)
    bounds_min_longitude = models.DecimalField(max_digits=8, decimal_places=5,
                                               null=True)
    bounds_max_latitude  = models.DecimalField(max_digits=7, decimal_places=5,
                                               null=True)
    bounds_max_longitude = models.DecimalField(max_digits=8, decimal_places=5,
                                               null=True)

#############################################################################

class Annotation(models.Model):
    """ A single posting annotation.

        An annotation consists of both a key and a value, for example, the key
        might be "color" and the value might be "blue".  These are combined
        into a single string with a colon between the two items, ie:

            color:blue

        Note that there is a many-to-many relationship between postings and
        annotations: an annotation can apply to multiple postings, and a single
        posting can have multiple annotations applied to it.
    """
    id         = models.AutoField(primary_key=True)
    annotation = models.TextField(db_index=True, unique=True)

#############################################################################

class Posting(models.Model):
    """ An individual posting in our database.
    """
    id                 = models.AutoField(primary_key=True)
    account_id         = models.TextField(null=True)
    source             = models.ForeignKey(Source,
                                           related_name="posting_source")
    category           = models.ForeignKey(Category,
                                           related_name="posting_category")
    category_group     = models.ForeignKey(CategoryGroup,
                                           related_name="posting_cat_group")
                                           
    location_latitude  = models.DecimalField(max_digits=7, decimal_places=5,
                                             null=True)
    location_longitude = models.DecimalField(max_digits=8, decimal_places=5,
                                             null=True)
    location_accuracy  = models.IntegerField(null=True)
    
    location_bounds    = models.TextField(null=True) # comma-separated values.
    location_country   = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_country")
    location_state     = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_state")
    location_metro     = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_metro")
    location_region    = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_region")
    location_county    = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_county")
    location_city      = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_city")
    location_locality  = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_locality")
    location_zipcode   = models.ForeignKey(Location, null=True, blank=True,
                                           related_name="posting_zipcode")

    external_id        = models.TextField()
    external_url       = models.TextField(null=True)
    heading            = models.TextField()
    # heading_tsv = tsvector() -- created by "0002_text_indexes" db migration.
    body               = models.TextField(null=True)
    # body_tsv = tsvector() -- created by "0002_text_indexes" db migration.
    html               = models.TextField(null=True)
    timestamp          = models.DateTimeField(db_index=True)
    inserted           = models.DateTimeField(db_index=True,
                                              default=datetime.datetime.now)
    expires            = models.DateTimeField(db_index=True)
    language           = models.TextField(null=True)
    price              = models.FloatField(null=True, db_index=True)
    currency           = models.TextField(null=True, db_index=True)
    status_offered     = models.BooleanField(default=False,
                                             db_index=True)
    status_wanted      = models.BooleanField(default=False,
                                             db_index=True)
    status_lost        = models.BooleanField(default=False,
                                             db_index=True)
    status_stolen      = models.BooleanField(default=False,
                                             db_index=True)
    status_found       = models.BooleanField(default=False,
                                             db_index=True)
    status_deleted     = models.BooleanField(default=False,
                                             db_index=True)
    has_image          = models.BooleanField(default=False,
                                             db_index=True)
    immortal           = models.BooleanField(default=False,
                                             db_index=True)

    class Meta:
        unique_together = ("source", "external_id")

#############################################################################

class PostingAnnotation(models.Model):
    """ A reference to an annotation within a posting.

        Note that each posting can have multiple annotations, and each
        annotation can appear in multiple postings.  This is a classic
        many-to-many relationship.
    """
    posting    = models.ForeignKey(Posting)
    annotation = models.ForeignKey(Annotation)

#############################################################################

class ImageReference(models.Model):
    """ A reference to an image associated with a posting.

        Note that each posting can have multiple image references associated
        with it.  Each image is available in full and thumbnail size.
    """
    posting          = models.ForeignKey(Posting)
    full_url         = models.TextField(null=True)
    full_width       = models.IntegerField(null=True)
    full_height      = models.IntegerField(null=True)
    thumbnail_url    = models.TextField(null=True)
    thumbnail_width  = models.IntegerField(null=True)
    thumbnail_height = models.IntegerField(null=True)

