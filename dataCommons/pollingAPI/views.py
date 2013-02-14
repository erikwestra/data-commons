""" dataCommons.pollingAPI.views

    This module implements the view functions for the "pollingAPI" application.
"""
import logging
import time

import simplejson as json

from django.conf                  import settings
from django.http                  import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db                    import connection, transaction
from django.db.utils              import DatabaseError

from dataCommons.shared.models          import *
from dataCommons.shared.lib.decorators  import *
from dataCommons.shared.lib             import dateHelpers

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

#def _p_resolve_base(posting_dict, posting_db):
#    posting_dict['category_group'] = posting_db.category_group.name
#    posting_dict['id']        = posting_db.id
#    posting_dict['category']  = posting_db.category.name
#    posting_dict['source']    = posting_db.source.code
#    posting_dict['heading']   = posting_db.heading
#    posting_dict['timestamp'] = str(posting_db.timestamp)
#    posting_dict['updated_at'] = str(posting_db.updated_at)
#    posting_dict['has_image'] = posting_db.has_image
#    
    # NOTE: 'inserted' is not correct db value for 'indexed' attr, it will be fixed soon.
    # posting_dict['inserted']   = str(posting_db.inserted)
#    posting_dict['indexed']   = str(posting_db.inserted)
#
#def _p_resolve_locs(posting_dict, posting_db):
#    l_attr = ('latitude', 'longitude', 'accuracy')
#
#    l_attr_code = ('country', 'state', 'metro', 'region', 'county', 'city',
#                   'locality', 'zipcode')
#
#    posting_dict['location'] = {}
#
#    for key in (l_attr + l_attr_code):
#        data = getattr(posting_db, 'location_' + key)
#        
#        if data is not None:
#            if key in l_attr:
#                posting_dict['location'][key] = data
#            else:
#                posting_dict['location'][key] = data.code
#
#def _p_resolve_annotaions(posting_dict, posting_db):
#    posting_dict['annotations'] = {}
#    posting_dict['annotations'].update(
#        map(
#            lambda ann: ann.annotation.annotation.split(":", 1),
#            posting_db.postingannotation_set.all()
#        )
#    )

#############################################################################

@csrf_exempt
@transaction.commit_manually
@print_exceptions_to_stdout_and_return_500
@log_sql_statements
def poll(request):
    """ Respond to the "/poll" URL.

        We return a list of the postings with the given timestamp
        We poll postings from given timestamp and rpp arguments.
    """

    now = time.time()

    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # avail. GET arguments
    rpp = None
    timestamp = None

    # Extract timestamp parameter.

    if "timestamp" in request.GET:
        try:
            timestamp = int(request.GET['timestamp'])
        except (ValueError, AttributeError):
            return HttpResponse(json.dumps(
                                  {'success' : False,
                                   'error'   : "Invalid 'timestamp' value"}),
                                mimetype="application/json")
    else:
        timestamp = int(now - 24*60*60) # 1 day ago.

    # Extract rpp parameter.

    if "rpp" in request.GET:
        try:
            rpp = int(request.GET['rpp'])
        except ValueError:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "Invalid 'rpp' value."}),
                                mimetype="application/json")

        if rpp < 1 or rpp > 1000:
            return HttpResponse(json.dumps(
                                    {'success': False,
                                     'error': "'rpp' value out of range"}),
                                mimetype="application/json")

    else:
        rpp = 1000

    # Construct a search query based on the supplied parameters.

    timestamp = dateHelpers.datetime_in_utc(timestamp)

    query = Posting.objects.filter(updated_at__gte=timestamp)
    query = query.order_by("-updated_at")
    query = query[:rpp]

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
    except DatabaseError,e:
        transaction.rollback()  # Let the database keep working.

        if "statement timeout" in str(e):
            # The query timed out. Tell the user the bad news.
            sql = str(query.query)
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
