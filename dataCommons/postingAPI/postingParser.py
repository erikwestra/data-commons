""" dataCommons.postingAPI.postingParser

    This module implements the logic for parsing incoming posting data.  Note
    that we validate the posting data as much as possible, including checking
    the source, category and location codes.

    Parsed Posting Format
    ---------------------

    When a posting is parsed, it is split into three parts:

        1. A dictionary holding the various fields of the core posting object.

        2. A list of annotation values to associate with this posting, where
           each annotation is a string of the form "key:value".

        3. A list of dictionaries holding the various images that were
           associated with this posting.

    These various parts are represented by a dictionary with the following
    entries:

        'posting'      ->  the core posting dictionary.
        'annotations'  ->  a list of annotation strings.
        'images'       ->  a list of image reference dictionaries.

    This dictionary will be passed on to the posting processor so that the
    posting can be added to the system.
"""
import decimal
import logging

from dataCommons.shared.models import *
from dataCommons.shared.lib    import dataCache, dateHelpers

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def check_raw_postings(raw_postings):
    """ Check that the given raw postings are acceptable.

        'raw_postings' should be a list of raw postings, where each raw posting
        is represented by a dictionary.

        Upon completion, we return a list of (success, result) tuples, one for
        each of the raw postings, where'success' is a boolean indicating
        whether or not that posting was acceptable, and 'result' is either the
        parsed form of that posting, as described above, or a string containing
        a suitable error message explaining why that posting was not
        acceptable.
    """
    source_codes    = get_source_codes()
    category_codes  = get_category_codes()
    category_groups = get_category_groups()
    country_codes   = None # Loaded into memory as required.
    state_codes     = None # ditto.
    metro_codes     = None # ditto.
    region_codes    = None # ditto.
    county_codes    = None # ditto.
    city_codes      = None # ditto.
    locality_codes  = None # ditto.
    zip_codes       = None # ditto.

    results = []
    for raw_posting in raw_postings:
        try:
            posting     = {}
            annotations = []
            images      = []

            if not isinstance(raw_posting, dict):
                raise ParsingException("Posting must be an object or " +
                                       "dictionary")

            remaining_fields = set(raw_posting.keys())

            parse_field(raw_posting, "account_id", posting, "account_id",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "source", posting, "source",
                        remaining_fields, required=True,
                        foreign_key=source_codes)

            parse_field(raw_posting, "category", posting, "category",
                        remaining_fields, foreign_key=category_codes)

            if "category" in raw_posting:
                posting['category_group_id'] = \
                    category_groups[raw_posting['category'].upper()]

            if "location" in raw_posting:
                raw_loc = raw_posting['location']
                remaining_fields.remove("location")

                remaining_loc_fields = set(raw_loc.keys())

                parse_field(raw_loc, "lat", posting, "location_latitude",
                            remaining_loc_fields, coerce_to_type="decimal",
                            min_value=-90, max_value=+90)

                parse_field(raw_loc, "long", posting, "location_longitude",
                            remaining_loc_fields, coerce_to_type="decimal",
                            min_value=-180, max_value=+180)

                parse_field(raw_loc, "accuracy", posting, "location_accuracy",
                            remaining_loc_fields, coerce_to_type="integer")

                if "bounds" in raw_loc:
                    # Manually copy across the bounds array.
                    posting['location_bounds'] = raw_loc['bounds']
                    remaining_loc_fields.remove("bounds")

                if "country" in raw_loc:
                    if country_codes == None:
                        country_codes = get_country_codes()

                    parse_field(raw_loc, "country", posting, "location_country",
                                remaining_loc_fields, foreign_key=country_codes)

                if "state" in raw_loc:
                    if state_codes == None:
                        state_codes = get_state_codes()

                    parse_field(raw_loc, "state", posting, "location_state",
                                remaining_loc_fields, foreign_key=state_codes)

                if "metro" in raw_loc:
                    if metro_codes == None:
                        metro_codes = get_metro_codes()

                    parse_field(raw_loc, "metro", posting, "location_metro",
                                remaining_loc_fields, foreign_key=metro_codes)

                if "region" in raw_loc:
                    if region_codes == None:
                        region_codes = get_region_codes()

                    parse_field(raw_loc, "region", posting, "location_region",
                                remaining_loc_fields, foreign_key=region_codes)

                if "county" in raw_loc:
                    if county_codes == None:
                        county_codes = get_county_codes()

                    parse_field(raw_loc, "county", posting, "location_county",
                                remaining_loc_fields, foreign_key=county_codes)

                if "city" in raw_loc:
                    if city_codes == None:
                        city_codes = get_city_codes()

                    parse_field(raw_loc, "city", posting, "location_city",
                                remaining_loc_fields, foreign_key=city_codes)

                if "locality" in raw_loc:
                    if locality_codes == None:
                        locality_codes = get_locality_codes()

                    parse_field(raw_loc, "locality", posting,
                                "location_locality", remaining_loc_fields,
                                foreign_key=locality_codes)

                if "zipcode" in raw_loc:
                    if zip_codes == None:
                        zip_codes = get_zip_codes()

                    parse_field(raw_loc, "zipcode", posting,
                                "location_zipcode", remaining_loc_fields,
                                foreign_key=zip_codes)

                if remaining_loc_fields:
                    raise ParsingException("Unexpected location field(s): " +
                                           ", ".join(remaining_loc_fields))

            parse_field(raw_posting, "external_id", posting, "external_id",
                        remaining_fields, required=True,
                        coerce_to_type="string")

            parse_field(raw_posting, "external_url", posting, "external_url",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "heading", posting, "heading",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "body", posting, "body",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "html", posting, "html",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "timestamp", posting, "timestamp",
                        remaining_fields, coerce_to_type="datetime")

            parse_field(raw_posting, "expires", posting, "expires",
                        remaining_fields, coerce_to_type="datetime")

            parse_field(raw_posting, "language", posting, "language",
                        remaining_fields, coerce_to_type="string")

            parse_field(raw_posting, "price", posting, "price",
                        remaining_fields, coerce_to_type="float")

            parse_field(raw_posting, "currency", posting, "currency",
                        remaining_fields, coerce_to_type="string")

            if "images" in raw_posting:
                raw_images = raw_posting['images']
                remaining_fields.remove("images")

                if not isinstance(raw_images, (list, tuple)):
                    raise ParsingException("images must be an array")

                for raw_image in raw_images:
                    remaining_image_fields = set(raw_image.keys())

                    image = {}

                    parse_field(raw_image, "full", image, "full_url",
                                remaining_image_fields,
                                coerce_to_type="string")

                    parse_field(raw_image, "full_width", image, "full_width",
                                remaining_image_fields,
                                coerce_to_type="integer")

                    parse_field(raw_image, "full_height", image, "full_height",
                                remaining_image_fields,
                                coerce_to_type="integer")

                    parse_field(raw_image, "thumbnail", image, "thumbnail_url",
                                remaining_image_fields,
                                coerce_to_type="string")

                    parse_field(raw_image, "thumbnail_width",
                                image, "thumbnail_width",
                                remaining_image_fields,
                                coerce_to_type="integer")

                    parse_field(raw_image, "thumbnail_height",
                                image, "thumbnail_height",
                                remaining_image_fields,
                                coerce_to_type="integer")

                    if remaining_image_fields:
                        raise ParsingException("Unexpected image field(s): " +
                                            ", ".join(remaining_image_fields))

                    images.append(image)

            if len(images) > 0:
                posting['has_image'] = True
            else:
                posting['has_image'] = False

            if "annotations" in raw_posting:
                raw_annotations = raw_posting['annotations']
                remaining_fields.remove("annotations")

                for key,value in raw_annotations.items():
                    if value == None: continue

                    if not isinstance(key, basestring):
                        raise ParsingException("Annotation keys must be " +
                                               "strings")

                    if not isinstance(value, basestring):
                        raise ParsingException("Annotation values must be " +
                                               "strings")

                    annotations.append(key + ":" + value)

            if "status" in raw_posting:
                raw_status = raw_posting['status']
                remaining_fields.remove("status")

                remaining_status_fields = set(raw_status.keys())

                parse_field(raw_status, "offered", posting, "status_offered",
                            remaining_status_fields, coerce_to_type="boolean")

                parse_field(raw_status, "wanted", posting, "status_wanted",
                            remaining_status_fields, coerce_to_type="boolean")

                parse_field(raw_status, "lost", posting, "status_lost",
                            remaining_status_fields, coerce_to_type="boolean")

                parse_field(raw_status, "stolen", posting, "status_stolen",
                            remaining_status_fields, coerce_to_type="boolean")

                parse_field(raw_status, "found", posting, "status_found",
                            remaining_status_fields, coerce_to_type="boolean")

                parse_field(raw_status, "deleted", posting, "status_deleted",
                            remaining_status_fields, coerce_to_type="boolean")

                if remaining_status_fields:
                    raise ParsingException("Unexpected status field(s): " +
                                        ", ".join(remaining_status_fields))

            parse_field(raw_posting, "immortal", posting, "immortal",
                        remaining_fields, coerce_to_type="boolean")

            if remaining_fields:
                raise ParsingException("Unexpected field(s): " +
                                    ", ".join(remaining_fields))
        except ParsingException,e:
            results.append((False, e.err_msg))
            continue

        parsed_posting = {'posting'     : posting,
                          'annotations' : annotations,
                          'images'      : images}

        results.append((True, parsed_posting))

    return results

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

class ParsingException(Exception):
    """ Private exception class to used to indicate that a parse failed.

        Parsing exception objects have an 'err_msg' attribute that holds the
        text of the error message to return back to the caller.
    """
    def __init__(self, err_msg):
        self.err_msg = err_msg

    def __str__(self):
        return self.err_msg

#############################################################################

def get_source_codes():
    """ Return a dictionary containing the valid source codes.

        We return a dictionary mapping each source code (in uppercase) to the
        Source record ID used for that source code.  The source code dictionary
        is automatically recalculated if it isn't in the cache.
    """
    source_codes = dataCache.get("source_codes")

    if source_codes == None:
        source_codes = {}
        for source in Source.objects.all():
            source_codes[source.code.upper()] = source.id
        dataCache.set("source_codes", source_codes)

    return source_codes

#############################################################################

def get_category_codes():
    """ Return a dictionary containing the valid category codes.

        We return a dictionary mapping each category code (in uppercase) to the
        Category record ID used for that category code.  The category code
        dictionary is automatically recalculated if it isn't in the cache.
    """
    category_codes = dataCache.get("category_codes")

    if category_codes == None:
        category_codes = {}
        for category in Category.objects.all():
            category_codes[category.code.upper()] = category.id
        dataCache.set("category_codes", category_codes)

    return category_codes

#############################################################################

def get_category_groups():
    """ Return dictionary mapping category code to category group record ID.

        We return a dictionary mapping each category code (in uppercase) to the
        CategoryGroup record ID used for that category code.  The category
        group dictionary is automatically recalculated if it isn't in the
        cache.
    """
    category_groups = dataCache.get("category_groups")

    if category_groups == None:
        category_groups = {}
        for category in Category.objects.all():
            category_groups[category.code.upper()] = category.group.id
        dataCache.set("category_groups", category_groups)

    return category_groups

#############################################################################

def get_country_codes():
    """ Return a dictionary containing the valid country codes.

        We return a dictionary mapping each country code (in uppercase) to the
        Location record ID used for that country code.  The country code
        dictionary is automatically recalculated if it isn't in the cache.
    """
    country_codes = dataCache.get("country_codes")

    if country_codes == None:
        country_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_COUNTRY):
            country_codes[loc.code.upper()] = loc.id
        dataCache.set("country_codes", country_codes)

    return country_codes

#############################################################################

def get_state_codes():
    """ Return a dictionary containing the valid state codes.

        We return a dictionary mapping each state code (in uppercase) to the
        Location record ID used for that state code.  The state code dictionary
        is automatically recalculated if it isn't in the cache.
    """
    state_codes = dataCache.get("state_codes")

    if state_codes == None:
        state_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_STATE):
            state_codes[loc.code.upper()] = loc.id
        dataCache.set("state_codes", state_codes)

    return state_codes

#############################################################################

def get_metro_codes():
    """ Return a dictionary containing the valid metro area codes.

        We return a dictionary mapping each metro area code (in uppercase) to
        the Location record ID used for that metro area code.  The metro area
        code dictionary is automatically recalculated if it isn't in the cache.
    """
    metro_codes = dataCache.get("metro_codes")

    if metro_codes == None:
        metro_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_METRO):
            metro_codes[loc.code.upper()] = loc.id
        dataCache.set("metro_codes", metro_codes)

    return metro_codes

#############################################################################

def get_region_codes():
    """ Return a dictionary containing the valid region codes.

        We return a dictionary mapping each region code (in uppercase) to the
        Location record ID used for that region code.  The region code
        dictionary is automatically recalculated if it isn't in the cache.
    """
    region_codes = dataCache.get("region_codes")

    if region_codes == None:
        region_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_REGION):
            region_codes[loc.code.upper()] = loc.id
        dataCache.set("region_codes", region_codes)

    return region_codes

#############################################################################

def get_county_codes():
    """ Return a dictionary containing the valid county codes.

        We return a dictionary mapping each county code (in uppercase) to the
        Location record ID used for that county code.  The county code
        dictionary is automatically recalculated if it isn't in the cache.
    """
    county_codes = dataCache.get("county_codes")

    if county_codes == None:
        county_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_COUNTY):
            county_codes[loc.code.upper()] = loc.id
        dataCache.set("county_codes", county_codes)

    return county_codes

#############################################################################

def get_city_codes():
    """ Return a dictionary containing the valid city codes.

        We return a dictionary mapping each city code (in uppercase) to the
        Location record ID used for that city code.  The city code dictionary
        is automatically recalculated if it isn't in the cache.
    """
    city_codes = dataCache.get("city_codes")

    if city_codes == None:
        city_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_CITY):
            city_codes[loc.code.upper()] = loc.id
        dataCache.set("city_codes", city_codes)

    return city_codes

#############################################################################

def get_locality_codes():
    """ Return a dictionary containing the valid locality codes.

        We return a dictionary mapping each locality code (in uppercase) to the
        Location record ID used for that locality code.  The locality code
        dictionary is automatically recalculated if it isn't in the cache.
    """
    locality_codes = dataCache.get("locality_codes")

    if locality_codes == None:
        locality_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_LOCALITY):
            locality_codes[loc.code.upper()] = loc.id
        dataCache.set("locality_codes", locality_codes)

    return locality_codes

#############################################################################

def get_zip_codes():
    """ Return a dictionary containing the valid zip codes.

        We return a dictionary mapping each zip code (in uppercase) to the
        Location record ID used for that zip code.  The zip code dictionary is
        automatically recalculated if it isn't in the cache.
    """
    zip_codes = dataCache.get("zip_codes")

    if zip_codes == None:
        zip_codes = {}
        for loc in Location.objects.filter(level=Location.LEVEL_ZIPCODE):
            zip_codes[loc.code.upper()] = loc.id
        dataCache.set("zip_codes", zip_codes)

    return zip_codes

#############################################################################

def parse_field(src_dict, src_key, dst_dict, dst_key, remaining_fields,
                required=False, coerce_to_type="string", foreign_key=None,
                min_value=None, max_value=None):
    """ Parse a single field.

        The parameters are as follows:

            'src_dict'

                A dictionary holding the raw (unparsed) data.

            'src_key'

                The name of the field in the source dictionary.

            'dst_dict'

                A dictionary which will hold the parsed version of the value.

            'dst_key'

                The name of the field in the destination dictionary in which to
                store this value.

            'remaining_fields'

                A set containing the names of the fields we haven't processed
                yet.

            'required'

                Is this field required?

            'coerce_to_type'

                Coerce the supplied value to the given type of data, if
                possible.  The following data types are currently supported:

                    "string"
                    "integer"
                    "float"
                    "decimal"
                    "boolean"
                    "datetime"

            'foreign_key'

                If supplied, this is a dictionary containing foreign key values
                to use for this field.  Each dictionary entry maps a foreign
                key value to its associated record ID.  Note that for foreign
                keys, we append "_id" to the end of dst_attr so that we set the
                internal record ID of the foreign key field directly.

            'min_value'

                If supplied, the field must be greater than or equal to this
                value.

            'max_value'

                If supplied, the field must be less than or equal to this
                value.

        We do the following to process the field:

            * If 'src_key' doesn't exist in 'src_dict' and 'required' is True,
              we raise a ParsingException with the appropriate error message.

            * If 'foreign_key' is not None, we see if the given field value
              (converted to uppercase) is in the supplied dictionary.  If
              so, we store the associated record ID into:

                  dst_dict[dst_key + "_id"]

              If not, we raise a ParsingException with an appropriate error
              message.

            * If the supplied value can't be coerced to the given data type, we
              raise a ParsingException with the appropriate error message.

            * If the supplied value isn't within the given min_value and
              max_value range, we raise a ParsingException with an appropriate
              error message.

            * Otherwise, the supplied value will be copied from the source
              dictionary to the destination dictionary.

            * If the supplied source value was copied across (either directly,
              or via a translation table), we remove the source field from
              'remaining_fields'.

        Note that no value is returned by this function; either an exception is
        raised or the function completes silently.
    """
    try:
        src_value = src_dict[src_key]
    except KeyError:
        src_value = None

    if src_value == None:
        if required:
            raise ParsingException("Missing required '%s' field" % src_key)
        else:
            return # Nothing else to do.

    if foreign_key != None:
        if isinstance(src_value, basestring):
            try:
                record_id = foreign_key[src_value.upper()]
            except KeyError:
                raise ParsingException("Unknown %s value: '%s'" % (src_key,
                                                                   src_value))
            dst_dict[dst_key + "_id"] = record_id
            remaining_fields.remove(src_key)
            return
        else:
            raise ParsingException(src_key + " must be a string")

    if coerce_to_type == "string":
        try:
            src_value = str(src_value)
        except ValueError:
            raise ParsingException("Unable to convert " + src_key +
                                   " to a string")
    elif coerce_to_type == "integer":
        try:
            src_value = int(src_value)
        except ValueError:
            raise ParsingException("Unable to convert " + src_key +
                                   " to an integer")
    elif coerce_to_type == "float":
        try:
            src_value = float(src_value)
        except ValueError:
            raise ParsingException("Unable to convert " + src_key +
                                   " to a floating point number")
    elif coerce_to_type == "decimal":
        try:
            src_value = decimal.Decimal(str(src_value))
        except decimal.InvalidOperation:
            raise ParsingException("Unable to convert " + src_key +
                                   " to a decimal value")
    elif coerce_to_type == "boolean":
        try:
            src_value = bool(src_value)
        except ValueError:
            raise ParsingException("Unable to convert " + src_key +
                                   " to a boolean")
    elif coerce_to_type == "datetime":
        src_value = dateHelpers.datetime_in_utc(src_value)
        if src_value == None:
            raise ParsingException("Unable to convert " + src_key +
                                   " to a datetime")
    else:
        raise RuntimeError("Unknown coerce_to_type: " + repr(coerce_to_type))

    if min_value != None:
        if src_value < min_value:
            raise ParsingException(src_key + " can't be less than " +
                                   str(min_value))

    if max_value != None:
        if src_value > max_value:
            raise ParsingException(src_key + " can't be more than " +
                                   str(max_value))

    dst_dict[dst_key] = src_value
    remaining_fields.remove(src_key)

