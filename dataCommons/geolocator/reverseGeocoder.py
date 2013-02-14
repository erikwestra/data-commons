""" dataCommons.geolocator.reverseGeocoder

    This module implements a reverse geocoder, converting an arbitrary lat/long
    coordinate (along with an accuracy or size indicator) into a list of
    matching 3taps location codes.
"""
from decimal import Decimal
import math
import random
import time

from django.contrib.gis.geos import *

from dataCommons.shared.models     import *
from dataCommons.geolocator.models import *

#############################################################################

# The following constant provides a list of location level names, sorted by
# size.

LEVEL_NAMES = ["country", "state", "metro", "region", "county", "city",
               "locality", "zipcode"]

#############################################################################

def calc_locations(latitude, longitude, bounds=None, accuracy=None):
    """ Calculate the matching locations for the given lat/long coordinate.

        The parameters are as follows:

            'latitude'

                The latitude of the desired coordinate, as a floating-point
                number.

            'longitude'

                The longitude of the desired coordinate, as a floating-point
                number.

            'bounds'

                A list of 4 coordinate values, representing the bounding box
                that completely encloses the feature found at the given
                coordinate.  If the bounding box is supplied, it should be of
                the form (min_lat, max_lat, min_long, max_long).

            'accuracy'

                An integer indicating the accuracy of the lat/long coordinate,
                if known.  This value is interpreted as follows:

                    0 = unknown.
                    1 = coordinate is accurate only to the country level.
                    2 = coordinate is accurate only to the state level.
                    3 = coordinate is accurate only to the metro area level.
                    4 = coordinate is accurate only to the region level.
                    5 = coordinate is accurate only to the county level.
                    6 = coordinate is accurate only to the city level.
                    7 = coordinate is accurate only to the locality level.
                    8 = coordinate is accurate to at least the ZIP code level.

        Taking the given lat/long coordinate, we find all 3taps locations that
        contain that coordinate.  We then filter this list to exclude locations
        that do not match the bounds or accuracy, if these are supplied.

        Upon completion, we return a dictionary with zero or more of the
        following entries:

            country
            state
            metro
            region
            county
            city
            locality
            zipcode

        Each entry will be a Location object identifying the matching location
        at that level.
    """
    # The following helper function converts from a Location.level value to a
    # level name.

    def calc_level_name(level_num):
        for level,name in Location.LEVEL_CHOICES:
            if level_num == level:
                return name
        return None

    # Start by finding all LocationMatch objects that contain the desired
    # coordinate.  These give us the locations that match the desired
    # coordinate, which we organise by level.

    matched_locations = {} # Maps level name to a dictionary mapping the 3taps
                           # location code to its associated Location object.

    coordinate = Point(longitude, latitude)
    for match in LocationMatch.objects.filter(outline__contains=coordinate):
        location = match.location
        level_name = calc_level_name(location.level)
        if level_name not in matched_locations:
            matched_locations[level_name] = {}
        matched_locations[level_name][location.code] = location

    # Based on the supplied bounds or accuracy, build a list of the location
    # levels to exclude from the results.

    include_all       = True # initially.
    levels_to_include = set()

    if bounds != None:

        include_all = False

        # Get the desired bounding box.  Note that we increase the bounds
        # by 10% to allow for differences in polygons, measurement errors, etc.

        bounds_min_lat  = bounds[0]
        bounds_max_lat  = bounds[1]
        bounds_min_long = bounds[2]
        bounds_max_long = bounds[3]

        extra_width  = (bounds_max_long - bounds_min_long) * 0.10
        extra_height = (bounds_max_lat - bounds_min_lat) * 0.10

        bounds_min_lat  = max(bounds_min_lat - extra_height, -90)
        bounds_max_lat  = min(bounds_max_lat + extra_height, +90)
        bounds_min_long = max(bounds_min_long - extra_width, -180)
        bounds_max_long = min(bounds_max_long + extra_width, +180)

        bounds_min_lat  = Decimal(str(bounds_min_lat))
        bounds_max_lat  = Decimal(str(bounds_max_lat))
        bounds_min_long = Decimal(str(bounds_min_long))
        bounds_max_long = Decimal(str(bounds_max_long))

        # Find the biggest matching location that fits inside our adjusted
        # bounds.  

        biggest_location_level = None

        for level_name in reversed(LEVEL_NAMES):
            if level_name not in matched_locations: continue
            loc_fits_in_bounds = False # Does at least one matched location at
                                       # this level fit within the bounds?
            for loc in matched_locations[level_name].values():
                if _rect_in_rect(loc.bounds_min_longitude,
                                 loc.bounds_min_latitude,
                                 loc.bounds_max_longitude,
                                 loc.bounds_max_latitude,
                                 bounds_min_long,
                                 bounds_min_lat,
                                 bounds_max_long,
                                 bounds_max_lat):
                    loc_fits_in_bounds = True
                    break

            if not loc_fits_in_bounds:
                # No location at this level fits inside the supplied bounds ->
                # the next lowest location level is the largest location that
                # fits.  Select that location level and all levels above it.
                i = LEVEL_NAMES.index(level_name)
                if i == 7:
                    biggest_location_level = 7
                else:
                    biggest_location_level = i + 1
                break

        # Include all locations at the biggest location level and higher.

        if biggest_location_level != None:
            for level in range(biggest_location_level+1):
                level_name = LEVEL_NAMES[level]
                if level_name in matched_locations:
                    levels_to_include.add(level_name)

    elif accuracy != None:

        if accuracy == 0:
            include_all = True
        else:
            include_all = False

        if accuracy >= 1:
            levels_to_include.add("country")
        if accuracy >= 2:
            levels_to_include.add("state")
        if accuracy >= 3:
            levels_to_include.add("metro")
        if accuracy >= 4:
            levels_to_include.add("region")
        if accuracy >= 5:
            levels_to_include.add("county")
        if accuracy >= 6:
            levels_to_include.add("city")
        if accuracy >= 7:
            levels_to_include.add("locality")
        if accuracy == 8:
            levels_to_include.add("zipcode")

    else:

        include_all = True

    # Remove the levels we're not interested in from the list of matched
    # locations.

    if not include_all:
        for level in LEVEL_NAMES:
            if level not in levels_to_include:
                if level in matched_locations:
                    del matched_locations[level]

    # Now that we have a list of matching locations trimmed by the supplied
    # bounds or accuracy.  Decide which of these locations to use for each
    # level.  Note that in theory we should only ever have one matching
    # location for each level; if we have multiple locations at a given level,
    # we record that fact and choose the first one.

    results = {}
    for level in LEVEL_NAMES:
        if level in matched_locations:
            if len(matched_locations[level]) == 1:
                loc = matched_locations[level].values()[0]
                results[level] = loc
            elif len(matched_locations[level]) > 1:
                print "Oops -- got multiple locations at the same level!"
                loc = matched_locations[level].values()[0]
                results[level] = loc

    return results

#############################################################################

def test(latitude, longitude, bounds=None, accuracy=None, show_results=True):
    """ Test wrapper to make it easier to see how the geolocator works.

        We call calc_locations() with the supplied parameters, and then (if
        show_results is True), print a list of the matching locations and their
        associated levels.
    """
    matching_locs = calc_locations(latitude, longitude, bounds, accuracy)
    if show_results:
        for level in LEVEL_NAMES:
            if level in matching_locs:
                loc = matching_locs[level]
                print "  %s = %s (%s)" % (level, loc.full_name, loc.code)

#############################################################################

def test_random(bounds=None, accuracy=None, show_results=True):
    """ Generate a random lat/long and geolocate it.

        If 'bounds' is specified, we calculate a random lat/long within it.
        Otherwise, we calculate a random lat/long coordinate within the
        bounding box of California.

        If 'show_results' is True, we print the coordinate and the found
        locations.
    """
    if bounds != None:
        latitude  = random.uniform(bounds[0], bounds[1])
        longitude = random.uniform(bounds[2], bounds[3])
    else:
        latitude  = random.uniform(32.710890, 41.965481)
        longitude = random.uniform(-123.980715, -114.609375)

    if show_results:
        print "lat = %0.4f, long = %0.4f" % (latitude, longitude)

    test(latitude=latitude,
         longitude=longitude,
         bounds=bounds,
         accuracy=accuracy,
         show_results=show_results)

#############################################################################

def test_multi(num_tests, bounds=None, accuracy=None, show_results=True):
    """ Call test_random() a number of times, and see how long it takes.
    """
    start_time = time.time()

    for test in range(num_tests):
        test_random(bounds=bounds,
                    accuracy=accuracy,
                    show_results=show_results)

    end_time = time.time()
    time_taken = end_time - start_time
    print "%d tests took %0.4f seconds" % (num_tests, time_taken)

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _rect_in_rect(left1, bottom1, right1, top1,
                  left2, bottom2, right2, top2):
    """ Return True iff rectangle 1 is inside rectangle 2.
    """
    if left1 >= left2 and right1 <= right2:
        if bottom1 >= bottom2 and top1 <= top2:
            return True
    return False

