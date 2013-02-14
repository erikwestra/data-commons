import logging
import time
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
from django.db.utils import DatabaseError
from django.utils import simplejson as json

from dataCommons.shared.models import *
from dataCommons.shared.lib.decorators import *
from dataCommons.shared.lib.dateHelpers import datetime_to_seconds, datetime_in_utc

logger = logging.getLogger(__name__)

# Complilling pattern for 'timestamp' parameter validation into constant to
# increase request processing speed. Pattern will be actual for a few
# hundred years.
TIMESTAMP_VALIDATE_PATTERN = re.compile(r"^(\d{10})$")

# Complilling pattern for 'timestamp' parameter validation into constant to
DB_TIMEOUT_PATTERN = re.compile("statement timeout")

# The oldest timestamp of the postings to return.
# MAX_TIMESTAMP_DIFF = 7 * 24 * 3600 # 7 days old

# Max. number of postings to return in response.
MAX_POSTINGS_NUMBER = 1000

# Default argument if timestamp is not passed to GET request.
DEFAULT_TIMESTAMP_DIFF = 24 * 3600

# Default posting number to return if it's not passed to GET request.
DEFAULT_POSTINGS_NUMBER = 1000

def _p_resolve_base(posting_dict, posting_db):
    posting_dict['category_group'] = posting_db.category_group.name
    posting_dict['id']        = posting_db.id
    posting_dict['category']  = posting_db.category.name
    posting_dict['source']    = posting_db.source.code
    posting_dict['heading']   = posting_db.heading
    posting_dict['timestamp'] = str(posting_db.timestamp)
    posting_dict['updated_at'] = str(posting_db.updated_at)
    posting_dict['has_image'] = posting_db.has_image
    
    # NOTE: 'inserted' is not correct db value for 'indexed' attr, it will be fixed soon.
    # posting_dict['inserted']   = str(posting_db.inserted)
    posting_dict['indexed']   = str(posting_db.inserted)

def _p_resolve_locs(posting_dict, posting_db):
    l_attr = ('latitude', 'longitude', 'accuracy')

    l_attr_code = ('country', 'state', 'metro', 'region', 'county', 'city',
                   'locality', 'zipcode')

    posting_dict['location'] = {}

    for key in (l_attr + l_attr_code):
        data = getattr(posting_db, 'location_' + key)
        
        if data is not None:
            if key in l_attr:
                posting_dict['location'][key] = data
            else:
                posting_dict['location'][key] = data.code

def _p_resolve_annotaions(posting_dict, posting_db):
    posting_dict['annotations'] = {}
    posting_dict['annotations'].update(
        map(
            lambda ann: ann.annotation.annotation.split(":", 1),
            posting_db.postingannotation_set.all()
        )
    )

@csrf_exempt
@transaction.commit_manually
@print_exceptions_to_stdout_and_return_500
@log_sql_statements
def poll(request):
    """
    Respond to the "/api/latest/poll" URL.

    We poll postings from given timestamp and rpp arguments.
    """

    now = time.time()
    # start_time = time.time()

    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # avail. GET arguments
    rpp = None
    timestamp = None

    # Extract timestamp parameter.

    if "timestamp" in request.GET:

        # try to extract timestamp from object
        match_obj = re.match(TIMESTAMP_VALIDATE_PATTERN, request.GET['timestamp'])

        try:
            timestamp = int(match_obj.group(1))
        except (ValueError, AttributeError):
            return HttpResponse(json.dumps(
                                        {'success': False,
                                         'error': "Invalid 'timestamp' value"}),
                                mimetype="application/json")

        # validate timestamp bounds
        if timestamp > now:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "'timestamp' value is out of bounds: %d" % timestamp}),
                                mimetype="application/json")
    else:
        timestamp = int(now - DEFAULT_TIMESTAMP_DIFF)

    # Extract rpp parameter.

    if "rpp" in request.GET:
        try:
            rpp = int(request.GET['rpp'])
        except ValueError:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "Invalid 'rpp' value."}),
                                mimetype="application/json")

        if rpp < 1 or rpp > MAX_POSTINGS_NUMBER:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "'rpp' value out of range"}),
                                mimetype="application/json")

    else:
        rpp = DEFAULT_POSTINGS_NUMBER

    # !!! NOTE: May be used soon.

    """
    # Extract old_format parameter.
    if "old_format" in request.GET:
        old_format = request.GET['old_format']

        eval_bool = {'0': False, 'false': False, 'False': False,
                     '1': True,  'true':  True,  'True':  True}

        old_format = eval_bool.get(old_format)

        if old_format is None:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "Invalid 'old_format' value."}),
                                mimetype="application/json")
    """

    # Construct a search query based on the supplied parameters.

    timestamp = datetime_in_utc(timestamp)
    # now = datetime_in_utc(now)

    # Go to order and filter by updated_at field.
    # Use only lower timestamp bound to allow poll postings "from future" 
    # (that bug occurs because of TZ defferences)
    # query = query.filter(timestamp__gte=timestamp, timestamp__lte=now)
    # query = query.order_by("-timestamp")
    query = Posting.objects.filter(updated_at__gte=timestamp)
    query = query.order_by("-updated_at")
    query = query[:rpp]

    # Testing: If the caller provided a "return_sql" parameter, return the raw
    # SQL statement rather than running it.

    # sql = str(query.query)
    # if (request.GET.get("return_sql") == "1"):
        # return HttpResponse(sql)

    # Before running the query, set a timeout so we don't hang if the query
    # takes too long.

    cursor = connection.cursor()
    cursor.execute("SET STATEMENT_TIMEOUT=%s" % settings.QUERY_TIMEOUT)

    # Process the search query, and assemble our search results.

    found_postings = []

    try:
        for posting in query:
            found_posting = {}
            _p_resolve_base(found_posting, posting)
            _p_resolve_locs(found_posting, posting)
            _p_resolve_annotaions(found_posting, posting)

            found_postings.append(found_posting)
    except DatabaseError, exc:
        transaction.rollback()  # Let the database keep working.

        # if "statement timeout" in str(exc):
        if re.search(DB_TIMEOUT_PATTERN, str(exc)):

            sql = str(query.query)
            # The query timed out. Tell the user the bad news.
            logger.debug("DATABASE TIMEOUT, query=" + sql)
            # eventRecorder.record("POLLING_API", "QUERY_TIMED_OUT", text=sql)
            transaction.commit()
            return HttpResponse(json.dumps({'success': False,
                                            'error': "Database timeout"}),
                                mimetype="application/json")
        else:
            return HttpResponse(json.dumps({'success': False,
                                            'error': "Database error"}),
                                mimetype="application/json")

    # Assemble our search response.

    response = {
        'success': True,
        'postings': found_postings
    }

    # Record an event telling us sql query.
    # eventRecorder.record("POLLING_API", "POLLING_REQUESTS", text=sql)

    transaction.commit()

    # Finally, return the response back to the caller.
    return HttpResponse(json.dumps(response, sort_keys=True, indent="    "),
                        mimetype="application/json")