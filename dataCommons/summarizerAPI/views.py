""" dataCommons.summarizerAPI.views

    This module defines the view functions made available by the Summarizer
    API.
"""
import logging
import time

from django.conf import settings

from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

from django.db.models import Count

from django.views.decorators.csrf import csrf_exempt

from django.db import connection, transaction
from django.db.utils import DatabaseError

import simplejson as json

from dataCommons.shared.models          import *
from dataCommons.shared.lib.decorators  import *
from dataCommons.shared.lib             import eventRecorder
from dataCommons.shared.lib             import searchHelpers

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

@csrf_exempt
@transaction.commit_manually
@print_exceptions_to_stdout_and_return_500
@log_sql_statements
def summarize(request):
    """ Respond to the "/api/latest/summarizer" URL.

        We calculate and return a summary of postings based on our supplied
        parameters.
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
                  "currency", "annotations", "status", "has_image",
                  "include_deleted"]:
        if param in request.GET:
            criteria[param] = request.GET[param]

    # Process our other parameters.

    if "dimension" in request.GET:
        dimension = request.GET['dimension']
        if dimension not in ["category", "location", "source"]:
            return HttpResponseBadRequest("Unknown dimension: " + dimension)
    else:
        return HttpResponseBadRequest("Missing required 'dimension' parameter")

    # Before running the query, set a timeout so we don't hang if the query
    # takes too long.

    cursor = connection.cursor()
    cursor.execute("SET STATEMENT_TIMEOUT=%s" % settings.QUERY_TIMEOUT)

    # Calculate the appropriate type of summary.

    if dimension == "category" and "category_group" not in criteria:
        success,results = _calc_category_group_summary(criteria)
    elif dimension == "category" and 'category_group' in criteria:
        success,results = _calc_category_summary(criteria)
    elif dimension == "location":
        success,results = _calc_location_summary(criteria)
    elif dimension == "source":
        success,results = _calc_source_summary(criteria)
    else:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : "Unable to determine " +
                                                    "summary type"}),
                            mimetype="application/json")

    # Record an event telling us how long the summary request took.

    end_time   = time.time()
    time_taken = int((end_time - start_time) * 1000) # Milliseconds.
    eventRecorder.record("SUMMARIZER_API", "SUMMARY_REQUESTS", 1, time_taken)
    transaction.commit()

    # Finally, return the results back to the caller.

    if success:
        return HttpResponse(json.dumps({'success' : True,
                                        'summary' : results},
                                       sort_keys=True, indent="    "),
                            mimetype="application/json")
    else:
        return HttpResponse(json.dumps({'success' : False,
                                        'error'   : results}),
                            mimetype="application/json")

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _calc_category_group_summary(criteria):
    """ Calculate and return a summary of postings by category group.

        'criteria' is a dictionary containing the supplied filter criteria.

        Upon completion, we return a (success, results) tuple, where 'success'
        is True if and only if the summary was successfully calculated.

        If 'success' is True, 'results' will be a list of (type, code, number)
        tuples, where 'type' is the type of summary item, 'code' is the 3taps
        code for that summary item, and 'number' is the number of matching
        postings.

        If 'success' is False, 'results' will be a string describing why the
        summary could not be calculated.
    """
    query = None # initially.

    try:
        success,results = searchHelpers.build_search_query(criteria)
        if not success:
            return (False, results)
        else:
            query = results

        query = query.values("category_group__code")

        results = []
        for row in query.annotate(count=Count("id")):
            results.append(("category_group",
                            row['category_group__code'],
                            row['count']))
    except DatabaseError,e:
        transaction.rollback() # Let the database keep working.
        if "statement timeout" in str(e):
            # The query timed out.  Tell the user the bad news.
            if query != None:
                sql = str(query.query)
                eventRecorder.record("SUMMARIZER_API", "QUERY_TIMED_OUT",
                                     text=sql)
                logger.debug("DATABASE TIMEOUT, query=" + sql)
                transaction.commit()
            return (False, "Database timeout")
        else:
            raise

    return (True, results)

#############################################################################

def _calc_category_summary(criteria):
    """ Calculate and return a summary of postings by category.

        'criteria' is a dictionary containing the supplied filter criteria.

        If 'success' is True, 'results' will be a list of (type, code, number)
        tuples, where 'type' is the type of summary item, 'code' is the 3taps
        code for that summary item, and 'number' is the number of matching
        postings.

        If 'success' is False, 'results' will be a string describing why the
        summary could not be calculated.
    """
    query = None # initially.

    try:
        success,results = searchHelpers.build_search_query(criteria)
        if not success:
            return (False, results)
        else:
            query = results

        query = query.values("category__code")

        results = []
        for row in query.annotate(count=Count("id")):
            results.append(("category",
                            row['category__code'],
                            row['count']))
    except DatabaseError,e:
        transaction.rollback() # Let the database keep working.
        if "statement timeout" in str(e):
            # The query timed out.  Tell the user the bad news.
            if query != None:
                sql = str(query.query)
                eventRecorder.record("SUMMARIZER_API", "QUERY_TIMED_OUT",
                                     text=sql)
                logger.debug("DATABASE TIMEOUT, query=" + sql)
                transaction.commit()
            return (False, "Database timeout")
        else:
            raise

    return (True, results)

#############################################################################

def _calc_location_summary(criteria):
    """ Calculate and return a summary of postings by location.

        'criteria' is a dictionary containing the supplied filter criteria.

        If 'success' is True, 'results' will be a list of (type, code, number)
        tuples, where 'type' is the type of summary item, 'code' is the 3taps
        code for that summary item, and 'number' is the number of matching
        postings.

        If 'success' is False, 'results' will be a string describing why the
        summary could not be calculated.
    """
    # See what level of location we want to summarize on.  This is based on the
    # lowest-level of the supplied criteria.

    if "locality" in criteria:
        level = "zipcode"
    elif "city" in criteria:
        level = "locality"
    elif "county" in criteria:
        level = "city"
    elif "region" in criteria:
        level = "county"
    elif "metro" in criteria:
        level = "region"
    elif "state" in criteria:
        level = "metro"
    elif "country" in criteria:
        level = "state"
    else:
        level = "country"

    # Repeatedly process locations at this level, and drill down if we need to
    # to get lower-level locations.

    filter_results = []
    null_fields    = []

    while True:

        # Start by making a database query for the matching postings at this
        # level.

        query = None # initially.

        try:
            success,results = searchHelpers.build_search_query(criteria)

            if not success:
                return (False, results)
            else:
                query = results

            kwargs = {}
            for field in null_fields:
                kwargs[field] = None
            query = query.filter(**kwargs)

            grouping_field = "location_" + level + "__code"

            query = query.values(grouping_field)

            # Process the search results at this level.  Note that we might
            # encounter a row where the location code is NULL -- if this
            # happens, we'll have to drill down to a lower level.

            drill_down = False # initially.
            for row in query.annotate(count=Count("id")):
                if row[grouping_field] == None:
                    # We have some postings which don't match this level -> we
                    # have to drill down further.
                    drill_down = True
                else:
                    # Add this row to the summary results.
                    filter_results.append((level,
                                           row[grouping_field],
                                           row['count']))
        except DatabaseError,e:
            transaction.rollback() # Let the database keep working.
            if "statement timeout" in str(e):
                # The query timed out.  Tell the user the bad news.
                if query != None:
                    sql = str(query.query)
                    eventRecorder.record("SUMMARIZER_API", "QUERY_TIMED_OUT",
                                         text=sql)
                    logger.debug("DATABASE TIMEOUT, query=" + sql)
                    transaction.commit()
                return (False, "Database timeout")
            else:
                raise

        # If we have to drill down, do so now.

        if drill_down:

            # Add this level's location to the list of "null fields".  These
            # are fields which must have the value NULL in subsequent searches
            # as we continue to drill down.

            null_fields.append("location_" + level)

            # Continue searching at the next lower level.

            if level == "country":
                level = "state"
            elif level == "state":
                level = "metro"
            elif level == "metro":
                level = "region"
            elif level == "region":
                level = "county"
            elif level == "county":
                level = "city"
            elif level == "city":
                level = "locality"
            elif level == "locality":
                level = "zipcode"
            elif level == "zipcode":
                # We've reached the bottom -> give up.
                break

            continue
        else:
            break

    return (True, filter_results)

#############################################################################

def _calc_source_summary(criteria):
    """ Calculate and return a summary of postings by data source.

        'criteria' is a dictionary containing the supplied filter criteria.

        If 'success' is True, 'results' will be a list of (type, code, number)
        tuples, where 'type' is the type of summary item, 'code' is the 3taps
        code for that summary item, and 'number' is the number of matching
        postings.

        If 'success' is False, 'results' will be a string describing why the
        summary could not be calculated.
    """
    query = None # initially.

    try:
        success,results = searchHelpers.build_search_query(criteria)
        if not success:
            return (False, results)
        else:
            query = results

        query = query.values("source__code")

        results = []
        for row in query.annotate(count=Count("id")):
            results.append(("source",
                            row['source__code'],
                            row['count']))
    except DatabaseError,e:
        transaction.rollback() # Let the database keep working.
        if "statement timeout" in str(e):
            # The query timed out.  Tell the user the bad news.
            if query != None:
                sql = str(query.query)
                eventRecorder.record("SUMMARIZER_API", "QUERY_TIMED_OUT",
                                     text=sql)
                logger.debug("DATABASE TIMEOUT, query=" + sql)
                transaction.commit()
            return (False, "Database timeout")
        else:
            raise

    return (True, results)

