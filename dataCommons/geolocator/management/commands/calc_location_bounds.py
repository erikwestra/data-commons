""" dataCommons.geolocator.management.commands.calc_location_bounds

    This module defines the "calc_location_bounds" management command used by
    the Data Commons system.  This imports the polygons from a given import
    file and stores the bounding box for each polygon into the Location record.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import *

from dataCommons.shared.models import Location

#############################################################################

class Command(BaseCommand):
    """ Our "calc_location_bounds" management command.
    """
    args = "polygon_file"
    help = "Calculates the location bounds from a list of polygons"

    def handle(self, *args, **kwargs):
        if len(args) == 0:
            raise CommandError("This command takes one parameter.")
        if len(args) > 1:
            raise CommandError("This command takes only one parameter.")

        f = file(args[0], "r")
        for line in f.readlines():
            loc_code,wkt = line.rstrip().split("\t", 1)
            self.stdout.write("Processing " + loc_code + "...")
            self.stdout.flush()

            # Get the Location object associated with this polygon.

            try:
                location = Location.objects.get(code=loc_code)
            except Location.DoesNotExist:
                self.stdout.write("Unknown location!\n")
                continue

            # Parse the WKT to get the underlying polygon

            outline = GEOSGeometry(wkt)

            # Get the polygon's bounds.

            min_long,min_lat,max_long,max_lat = outline.extent

            # Store the polygon's bounds into the Location record.

            location.bounds_min_latitude  = Decimal(str(min_lat))
            location.bounds_min_longitude = Decimal(str(min_long))
            location.bounds_max_latitude  = Decimal(str(max_lat))
            location.bounds_max_longitude = Decimal(str(max_long))
            location.save()

            self.stdout.write("done\n")

