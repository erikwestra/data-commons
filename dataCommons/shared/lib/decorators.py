""" dataCommons.shared.lib.decorators

    This module defines various decorators that make it easier to implement
    view and other functions.
"""
import functools
import logging
import traceback

from django.http import HttpResponseServerError
from django.conf import settings
from django.db   import connection

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def print_exceptions_to_stdout(f):
    """ Decorator to print exceptions to stdout and silently return None.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
            return None
    return wrapper

#############################################################################

def print_exceptions_to_stdout_and_return_500(f):
    """ Decorator to print exceptions to stdout and return a 500 HTTP response.

        This is useful for wrapping Django view functions.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
            return HttpResponseServerError()
    return wrapper

#############################################################################

def log_sql_statements(f):
    """ Decorator to log SQL queries while running a function.

        The queries are written out to our query log if ENABLE_QUERY_LOGGING is
        set to True.

        This can be useful for identifying performance issues with the
        database.

        Inspired by: http://stackoverflow.com/questions/4115462
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if settings.ENABLE_QUERY_LOGGING:
            try:
                debug = settings.DEBUG
                settings.DEBUG = True
                connection.queries = []
                return f(*args, **kwargs)
            finally:
                if len(connection.queries) > 0:
                    logger.debug("============================================")
                    logger.debug("%d SQL statements executed by %s:" %
                                 (len(connection.queries), f.__name__))
                    total_time = 0.0
                    for query in connection.queries:
                        query_time = float(query['time'])
                        total_time = total_time + query_time
                        logger.debug("[%s] %s" % (query['time'], query['sql']))
                    logger.debug("total time taken = " + str(total_time) +
                                 " seconds")
                    logger.debug("============================================")
                settings.DEBUG = debug
        else:
            return f(*args, **kwargs)

    return wrapper

