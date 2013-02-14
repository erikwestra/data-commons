""" dataCommons.searchAPI.views

    This module defines the view functions made available by the Search API.
"""
import logging
import time

from datetime import datetime, timedelta

from django.conf import settings

from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt

from django.db import connection, transaction
from django.db.utils import DatabaseError

import simplejson as json

from dataCommons.shared.models          import *
from dataCommons.shared.lib.decorators  import *
from dataCommons.shared.lib             import eventRecorder
from dataCommons.shared.lib             import searchHelpers
from dataCommons.shared.lib.dateHelpers import datetime_to_seconds

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

@csrf_exempt
@print_exceptions_to_stdout_and_return_500
@log_sql_statements
def search(request):
    """ Respond to the "/api/latest/search" URL.

        We search for postings based on the given search criteria.
    """
    start_time = time.time()

    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # Check the caller's authentication.

    # ...eventually.

    # Extract the search criteria.

    criteria = {}

    for param in ["category_group", "category", "country", "state", "metro",
                  "region", "county", "city", "locality", "zipcode", "source",
                  "heading", "body", "text", "timestamp", "id", "price",
                  "currency", "annotations", "external_id", "status",
                  "has_image", "include_deleted", "only_deleted"]:
        if param in request.GET:
            criteria[param] = request.GET[param]

    # If the caller didn't supply a timestamp, add a default timestamp to the
    # search query.

    if "timestamp" not in criteria:
        criteria['timestamp'] = str(int((time.time() - 24*3600))) + '..' + \
                                str(int(time.time()))

    # Extract our other parameters.

    if "rpp" in request.GET:
        try:
            rpp = int(request.GET['rpp'])
        except ValueError:
            return HttpResponse(json.dumps(
                                    {'success' : False,
                                     'error'   : "Invalid 'rpp' value"}),
                                mimetype="application/json")
        if rpp < 1 or rpp > 100:
            return HttpResponse(json.dumps(
                                    {'success' : False,
                                     'error'   : "'rpp' value out of range"}),
                                mimetype="application/json")
    else:
        rpp = 10

    if "retvals" in request.GET:
        retvals = set()
        for field in request.GET['retvals'].split(","):
            if field in ["id", "account_id", "source", "category",
                         "category_group", "location", "external_id",
                         "external_url", "heading", "body", "html",
                         "timestamp", "expires", "language", "price",
                         "currency", "images", "annotations", "status",
                         "immortal"]:
                retvals.add(field)
            else:
                return HttpResponse(json.dumps(
                                        {'success' : False,
                                         'error'   : "invalid 'retvals' " +
                                                     "value: " + repr(field)}),
                                    mimetype="application/json")
    else:
        retvals = set(["id", "source", "category", "location", "external_id",
                       "external_url", "heading", "timestamp"])

    if "anchor" in request.GET:
        anchor = request.GET['anchor']
    else:
        anchor = None

    if "page" in request.GET:
        try:
            page = int(request.GET['page'])
        except ValueError:
            return HttpResponse(json.dumps(
                                    {'success' : False,
                                     'error'   : "Invalid 'page' value"}),
                                mimetype="application/json")
    else:
        page = 0

    # Construct a search query based on the supplied parameters.

    success,result = searchHelpers.build_search_query(criteria)

    if not success:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : result}),
                            mimetype="application/json")
    else:
        query = result

    if anchor != None:
        query = query.filter(id__lte=anchor)

    num_matches = query.count()

    query = query.order_by("-timestamp")
    query = query[page*rpp:page*rpp+rpp]
    sql = str(query.query)

    # Testing: If the caller provided a "return_sql" parameter, return the raw
    # SQL statement rather than running it.

    if (request.GET.get("return_sql") == "1"):
        return HttpResponse(sql)

    # Before running the query, set a timeout so we don't hang if the query
    # takes too long.

    cursor = connection.cursor()
    cursor.execute("SET STATEMENT_TIMEOUT=%s" % settings.QUERY_TIMEOUT)

    # Process the search query, and assemble our search results.

    found_postings = []
    new_anchor = None

    try:
        for posting in query:
            if anchor == None and new_anchor == None:
                # Remember the ID of the first (ie, most recent) found posting.
                # This will be our anchor for subsequent requests.
                new_anchor = str(posting.id)

            found_posting = {}
            if "id" in retvals:
                found_posting['id'] = posting.id
            if "account_id" in retvals:
                found_posting['account_id'] = posting.account_id
            if "source" in retvals:
                found_posting['source'] = posting.source.code
            if "category" in retvals:
                found_posting['category'] = posting.category.code
            if "category_group" in retvals:
                found_posting['category_group'] = posting.category_group.code
            if "location" in retvals:
                loc = {}
                if posting.location_latitude != None:
                    loc['latitude'] = posting.location_latitude
                if posting.location_longitude != None:
                    loc['longitude'] = posting.location_longitude
                if posting.location_accuracy != None:
                    loc['accuracy'] = posting.location_accuracy
                if posting.location_country != None:
                    loc['country'] = posting.location_country.code
                if posting.location_state != None:
                    loc['state'] = posting.location_state.code
                if posting.location_metro != None:
                    loc['metro'] = posting.location_metro.code
                if posting.location_region != None:
                    loc['region'] = posting.location_region.code
                if posting.location_county != None:
                    loc['county'] = posting.location_county.code
                if posting.location_city != None:
                    loc['city'] = posting.location_city.code
                if posting.location_locality != None:
                    loc['locality'] = posting.location_locality.code
                if posting.location_zipcode != None:
                    loc['zipcode'] = posting.location_zipcode.code
                found_posting['location'] = loc
            if "external_id" in retvals:
                found_posting['external_id'] = posting.external_id
            if "external_url" in retvals:
                found_posting['external_url'] = posting.external_url
            if "heading" in retvals:
                found_posting['heading'] = posting.heading
            if "body" in retvals:
                found_posting['body'] = posting.body
            if "html" in retvals:
                found_posting['html'] = posting.html
            if "timestamp" in retvals:
                found_posting['timestamp'] = datetime_to_seconds(
                                                        posting.timestamp)
            if "expires" in retvals:
                found_posting['expires'] = datetime_to_seconds(posting.expires)
            if "language" in retvals:
                found_posting['language'] = posting.language
            if "price" in retvals:
                found_posting['price'] = posting.price
            if "currency" in retvals:
                found_posting['currency'] = posting.currency
            if "images" in retvals:
                images = []
                for image in posting.imagereference_set.all():
                    dst_image = {}
                    if image.full_url != None:
                        dst_image['full_url'] = image.full_url
                    if image.full_width != None:
                        dst_image['full_width'] = image.full_width
                    if image.full_height != None:
                        dst_image['full_height'] = image.full_height
                    if image.thumbnail_url != None:
                        dst_image['thumbnail_url'] = image.thumbnail_url
                    if image.thumbnail_width != None:
                        dst_image['thumbnail_width'] = image.thumbnail_width
                    if image.thumbnail_height != None:
                        dst_image['thumbnail_height'] = image.thumbnail_height
                    images.append(dst_image)
                found_posting['images'] = images
            if "annotations" in retvals:
                annotations = {}
                for posting_annotation in posting.postingannotation_set.all():
                    s = posting_annotation.annotation.annotation
                    key,value = s.split(":", 1)
                    annotations[key] = value
                found_posting['annotations'] = annotations
            if "status" in retvals:
                status = {}
                status['offered'] = posting.status_offered
                status['lost']    = posting.status_lost
                status['stolen']  = posting.status_stolen
                status['found']   = posting.status_found
                status['deleted'] = posting.status_deleted
                found_posting['status'] = status
            if "immortal" in retvals:
                found_posting['immortal'] = posting.immortal

            found_postings.append(found_posting)
    except DatabaseError, e:
        if "statement timeout" in str(e):
            # The query timed out.  Tell the user the bad news.
            sql = str(query.query)
            logger.debug("DATABASE TIMEOUT, query=" + sql)
            eventRecorder.record("SEARCH_API", "QUERY_TIMED_OUT", text=sql)
            return HttpResponse(json.dumps({'success' : False,
                                            'error'   : "Database timeout"}),
                                mimetype="application/json")
        else:
            logger.exception(e)
            sql = str(query.query)
            return HttpResponse(json.dumps({'success' : False,
                                            'error'   : "Database error"}),
                                mimetype="application/json")

    # Assemble our search response.

    response = {'success'     : True,
                'num_matches' : num_matches,
                'postings'    : found_postings}

    if anchor == None and new_anchor != None:
        response['anchor'] = new_anchor

    # If the caller gave us an anchor, see if any new postings have come in
    # since the original query was made.

    if anchor != None:
        success,query = searchHelpers.build_search_query(criteria)
        if success:
            response['new_postings'] = query.filter(id__gt=anchor).count()

    # Record an event telling us how long the search request took.

    end_time   = time.time()
    time_taken = int((end_time - start_time) * 1000) # Milliseconds.
    eventRecorder.record("SEARCH_API", "SEARCH_REQUESTS", 1, time_taken,
                         text=sql)
    # transaction.commit()

    # Add the search request time to the response.

    response['time_taken'] = time_taken

    # Finally, return the response back to the caller.

    return HttpResponse(json.dumps(response, sort_keys=True, indent="    "),
                        mimetype="application/json")

