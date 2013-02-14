""" dataCommons.monitoringAPI.actions.event_recorder

    This module implements the internal logic for recording events.
"""
import datetime
import logging

from dataCommons.shared.lib import dateHelpers

from dataCommons.monitoringAPI.models import *

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def record(source, type, primary_value=None, secondary_value=None, text=None):
    """ Record the occurrence of an event.

        The parameters are as follows:

            'source'

                A string indicating the source of this event.

            'type'

                A string indicating the type of event.

            'primary_value'

                An integer giving the primary value for this event, if any.

            'secondary_value'

                An integer giving the secondary value for this event, if any.

            'text'

                Some optional text to associate with this event, if any.

        We create a new event with the given values and add it to the database.
        Upon completion, we return None if the event was successfully added, or
        an appropriate error message if something went wrong.
    """
    # Check that the parameters are correct.

    if source not in ["POSTING_API",
                      "SEARCH_API",
                      # "POLLING_API",
                      "SUMMARIZER_API"]:
        return "Unknown source: " + repr(source)

    if type == "POSTINGS_QUEUED":
        if primary_value == None:
            return "Missing required primary value"
        if secondary_value == None:
            return "Missing required secondary value"
        if text != None:
            return "This event type doesn't take any text"
    elif type == "POSTINGS_DEQUEUED":
        if primary_value == None:
            return "Missing required primary value"
        if secondary_value != None:
            return "This event type doesn't take a secondary value"
        if text != None:
            return "This event type doesn't take any text"
    elif type == "POSTINGS_PROCESSED":
        if primary_value == None:
            return "Missing required primary value"
        if secondary_value == None:
            return "Missing required secondary value"
        if text != None:
            return "This event type doesn't take any text"
    elif type == "SEARCH_REQUESTS":
        if primary_value == None:
            return "Missing required primary value"
        if secondary_value == None:
            return "Missing required secondary value"
    elif type == "SUMMARY_REQUESTS":
        if primary_value == None:
            return "Missing required primary value"
        if secondary_value == None:
            return "Missing required secondary value"
        if text != None:
            return "This event type doesn't take any text"
    elif type == "QUERY_TIMED_OUT":
        if primary_value != None:
            return "This event type doesn't take a primary value"
        if secondary_value != None:
            return "This event type doesn't take a secondary value"
        if text == None:
            return "This event type requires a text value"
    else:
        return "Unknown event type: " + type

    # Translate our event source and type into EventSource and EventType
    # objects, creating new records as required.

    event_source,created = EventSource.objects.get_or_create(source=source)
    event_type,created   = EventType.objects.get_or_create(type=type)

    # Create the new Event object.

    event = Event()
    event.timestamp       = dateHelpers.datetime_in_utc()
    event.source          = event_source
    event.type            = event_type
    event.primary_value   = primary_value
    event.secondary_value = secondary_value
    event.text            = text
    event.save()

    # That's all, folks!

    logger.debug("Received event %s from %s, values = %s"
                 % (type, source, str([primary_value, secondary_value, text])))

    return None

