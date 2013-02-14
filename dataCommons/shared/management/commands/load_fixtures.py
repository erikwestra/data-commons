""" dataCommons.shared.management.commands.load_fixtures

    This module defines the "load_fixtures" management command used by the Data
    Commons system.  Running this command loads the various fixtures into the
    database.
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management      import call_command

from dataCommons.shared.lib import dataCache

#############################################################################

# The following list defines the various fixture files to load into the
# database:

FIXTURES = ["categoryGroups.json",
            "categories.json",
            "sources.json",
            "locations.json"]

#############################################################################

class Command(BaseCommand):
    """ Our "load_fixtures" management command.
    """
    args = 'none'
    help = 'Loads our various fixtures into the database.'

    def handle(self, *args, **kwargs):
        if len(args) > 0:
            raise CommandError("This command doesn't take any parameters.")

        for fixture in FIXTURES:
            self.stdout.write("Loading data from " + fixture + "\n")
            call_command("loaddata", fixture)

