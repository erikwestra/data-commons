""" dataCommons.shared.management.commands.flush_cache

    This module defines the "flush_cache" management command used by the Data
    Commons system.  Running this command flushes the internal Redis caches
    used by the DataCache module.
"""
from django.core.management.base import BaseCommand, CommandError

from dataCommons.shared.lib import dataCache

#############################################################################

class Command(BaseCommand):
    """ Our "flush_cache" management command.
    """
    args = 'none'
    help = 'Flushes the internal Redis cache used by the DataCommons system.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        dataCache.flush()

