""" dataCommons.geolocator.models

    This file contains the Django models used by the "geolocator" application.
"""
from django.contrib.gis.db import models

#############################################################################

class LocationMatch(models.Model):
    """ A match against all or part of a location's outline.

        Each location match defines a location and an outline which covers all
        or part of the location.  Note that the location outline is split into
        rectangular sections and each section treated as a separate match to
        improve performance.
    """
    location = models.ForeignKey("shared.Location")
    outline  = models.MultiPolygonField(srid=4326)

    # Define a custom GeoManager to handle spatial queries against this table:

    objects = models.GeoManager()

