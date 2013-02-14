""" dataCommons.shared.management.commands.fix_has_image

    This module defines the "fix_has_image" management command used by the Data
    Commons system.  Running this command sets the "has_image" field for each
    posting to the appropriate value.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from dataCommons.shared.models import *

#############################################################################

class Command(BaseCommand):
    """ Our "flush_cache" management command.
    """
    args = 'none'
    help = "Sets each posting's has_image field to the appropriate value."

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        cursor = connection.cursor()

        self.stdout.write("Deleting index on 'has_image'...\n")

        cursor.execute("DROP INDEX shared_posting_has_image")
        transaction.commit_unless_managed()

        self.stdout.write("Setting 'has_image' to False...\n")

        Posting.objects.all().update(has_image=False) # initially.

        self.stdout.write("Gathering postings with images...\n")

        all_image_refs       = ImageReference.objects.all()
        postings_with_images = Posting.objects.filter(
                                    imagereference__in=all_image_refs)

        self.stdout.write("Updating 'has_image' for postings with images...\n")

        postings_with_images.update(has_image=True)

        self.stdout.write("Recreating 'has_index' index...\n")

        cursor.execute("CREATE INDEX shared_posting_has_image " +
                       "ON shared_posting USING btree(has_image)")
        transaction.commit_unless_managed()

        self.stdout.write("Done!\n")

