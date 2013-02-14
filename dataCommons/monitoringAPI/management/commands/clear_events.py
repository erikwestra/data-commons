""" dataCommons.shared.management.commands.clear_events

    This module defines the "clear_events" management command used by the Data
    Commons system.  Running this command removes all existing event logs and
    associated data from the system.
"""
from django.core.management.base import BaseCommand, CommandError

from dataCommons.monitoringAPI.models import *

#############################################################################

class Command(BaseCommand):
    """ Our "clear_events" management command.
    """
    args = 'none'
    help = 'Deletes all the event logs and associated data from the system.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        EventSource.objects.all().delete()
        EventType.objects.all().delete()
        Event.objects.all().delete()

