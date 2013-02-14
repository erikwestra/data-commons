""" dataCommons.shared.management.commands.flush_posting_queue

    This module defines the "flush_posting_queue" management command used by
    the Data Commons system.  Running this command flushes the internal queue
    of unprocessed postings.
"""
from django.core.management.base import BaseCommand, CommandError

import celery.task.control

#############################################################################

class Command(BaseCommand):
    """ Our "flush_posting_queue" management command.
    """
    args = 'none'
    help = 'Flushes the internal queue of unprocessed postings.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        celery.task.control.discard_all()

