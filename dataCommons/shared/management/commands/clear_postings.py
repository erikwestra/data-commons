""" dataCommons.shared.management.commands.clear_postings

    This module defines the "clear_postings" management command used by the
    Data Commons system.  Running this command removes all existing postings
    and associated data from the system.
"""
from django.core.management.base import BaseCommand, CommandError

from dataCommons.shared.models import *

#############################################################################

class Command(BaseCommand):
    """ Our "clear_postings" management command.
    """
    args = 'none'
    help = 'Deletes all the postings and associated data from the system.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        ImageReference.objects.all().delete()
        PostingAnnotation.objects.all().delete()
        Posting.objects.all().delete()
        Annotation.objects.all().delete()

