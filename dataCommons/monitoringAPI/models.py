""" dataCommons.monitoringAPI.models

    This file contains the Django models used by the "monitoringAPI"
    application.
"""
from django.db import models

#############################################################################

class EventSource(models.Model):
    """ The EventSource identifies the source of a recorded event.

        We keep these in a separate table to allow for fast lookups on events
        by source.
    """
    id     = models.AutoField(primary_key=True)
    source = models.TextField(db_index=True, unique=True)

#############################################################################

class EventType(models.Model):
    """ The EventType identifies the type of event which was recorded.

        We keep these in a separate table to allow for fast lookups on events
        by type.
    """
    id   = models.AutoField(primary_key=True)
    type = models.TextField(db_index=True, unique=True)

#############################################################################

class Event(models.Model):
    """ An event that was recorded by the Monitoring API.
    """
    id              = models.AutoField(primary_key=True)
    timestamp       = models.DateTimeField(db_index=True)
    source          = models.ForeignKey(EventSource)
    type            = models.ForeignKey(EventType)
    primary_value   = models.IntegerField(null=True)
    secondary_value = models.IntegerField(null=True)
    text            = models.TextField(null=True)

