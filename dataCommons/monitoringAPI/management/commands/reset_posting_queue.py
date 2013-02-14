""" dataCommons.shared.management.commands.reset_posting_queue

    This module defines the "reset_prosting_queue" management command used by
    the Data Commons system.  Running this command works around a bug where the
    number of "POSTINGS_DEQUEUED" events don't match the number of
    "POSTINGS_QUEUED" events, even when all postings have been processed.  We
    add a "POSTINGS_DEQUEUED" event to reset the number of postings back to
    zero.

    Note that this should only be run when there are no postings coming in from
    the Grabbers.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from dataCommons.monitoringAPI.models import *

from dataCommons.shared.lib import dateHelpers

#############################################################################

class Command(BaseCommand):
    """ Our "reset_posting_queue" management command.
    """
    args = 'none'
    help = 'Resets the posting queue down to zero.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        # Get the "POSTINGS_QUEUED" and "POSTINGS_DEQUEUED" event types.  We'll
        # need these for our various database queries.

        try:
            postings_queued_event = EventType.objects.get(
                                                    type="POSTINGS_QUEUED")
        except EventType.DoesNotExist:
            postings_queued_event = None

        try:
            postings_dequeued_event = EventType.objects.get(
                                                    type="POSTINGS_DEQUEUED")
        except EventType.DoesNotExist:
            postings_dequeued_event = None

        # Get the total number of postings which have been queued.

        if postings_queued_event != None:
            query = Event.objects.filter(type=postings_queued_event)
            num_postings_added = \
                query.aggregate(Sum("primary_value"))['primary_value__sum']
            if num_postings_added == None: num_postings_added = 0
        else:
            num_postings_added = 0

        # Get the total number of postings which have been dequeued.

        if postings_dequeued_event != None:
            query = Event.objects.filter(type=postings_dequeued_event)
            num_postings_removed = \
                query.aggregate(Sum("primary_value"))['primary_value__sum']
            if num_postings_removed == None: num_postings_removed = 0
        else:
            num_postings_removed = 0

        # Calculate the number of left-over postings.

        postings_to_remove = num_postings_added - num_postings_removed

        if postings_to_remove == 0:
            raise CommandError("There are no postings to remove!")

        # Finally, add a new "POSTINGS_DEQUEUED" event to reset the number of
        # postings back to zero.

        if postings_dequeued_event == None:
            postings_dequeued_event = EventType()
            postings_dequeued_event.type = "POSTINGS_DEQUEUED"
            postings_dequeued_event.save()

        posting_api_source = EventSource.objects.get_or_create(
                                                source="POSTING_API")[0]

        event = Event()
        event.timestamp     = dateHelpers.datetime_in_utc()
        event.type          = postings_dequeued_event
        event.source        = posting_api_source
        event.primary_value = num_postings_added - num_postings_removed
        event.save()

