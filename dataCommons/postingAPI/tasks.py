""" dataCommons.postingAPI.tasks

    This module implements the background tasks run by the Celery task queuing
    system.
"""
import logging

from celery import task

from dataCommons.shared.lib.decorators import print_exceptions_to_stdout

from dataCommons.postingAPI import postingProcessor

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################


@task()
@print_exceptions_to_stdout
def process_postings(parsed_postings):
    """ Process the given set of postings.

        Note that we simply call the posting processor to do all the work, but
        wrap it up in a Huey command so that the work is queued, and use the
        'print_exceptions_to_stdout' decorator so that any exceptions will be
        logged to stdout rather than written to the Huey log file (which won't
        exist when the system is deployed to Heroku).
    """
    postingProcessor.process_postings(parsed_postings)
