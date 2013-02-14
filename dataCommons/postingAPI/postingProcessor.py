""" dataCommons.postingAPI.postingProcessor

    This module implements the logic for processing the parsed postings. We
    geolocate the postings as required and insert them into the database.
"""
import logging
import time
import traceback

import newrelic.agent

from django.db import transaction,DatabaseError

from dataCommons.shared.models import *
from dataCommons.shared.lib import eventRecorder, dateHelpers
from dataCommons.shared.lib.decorators import *

from dataCommons.geolocator import reverseGeocoder

#############################################################################

# How many postings to process before committing our changes to the database:

MAX_NUM_POSTINGS_IN_TRANSACTION = 10

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

@transaction.commit_manually
#@log_sql_statements
@newrelic.agent.function_trace()
def process_postings(parsed_postings):
    """ Process a batch of parsed postings.

        'parsed_postings' should be a list of postings that have been
        successfully checked by the posting parser. Each entry in this list
        will be a dictionary with the following entries:

            'posting'

                The posting itself, as a dictionary. The fields in this
                dictionary match the attributes with the same name in the
                Posting object.

            'annotations'

                A list of annotation values to associate with this posting.
                Each string will be of the form "key:value"

            'images'

                A list of images to associate with this posting. Each image
                will be a dictionary with 'full_url' and 'thumbnail_url'
                entries, as appropriate.

        We process the postings, adding them to the system as appropriate.
        Note that this involves the following steps:

            1. Calling the Geolocator API if the postings need to be
               geolocated.

            2. Storing the postings into the database.

            3. Sending the postings out via the Notification API.
    """
    eventRecorder.record("POSTING_API", "POSTINGS_DEQUEUED",
                         len(parsed_postings))

    start_time = time.time()

    # If necessary, geolocate the postings.

    try:
        for src in parsed_postings:
            posting = src['posting']

            has_lat_long = False # initially.
            if ("location_latitude" in posting and 
                "location_longitude" in posting):
                has_lat_long = True

            has_loc_codes = False # initially.
            for field in ["location_country", "location_state",
                          "location_metro", "location_region",
                          "location_county", "location_city",
                          "location_locality", "location_zipcode"]:
                if field in posting:
                    has_loc_codes = True
                    break

            if has_lat_long and not has_loc_codes:
                # This posting has a lat/long value but no location codes ->
                # reverse geocode the posting to see which locations it belongs
                # to.
                locs = reverseGeocoder.calc_locations(
                                float(posting['location_latitude']),
                                float(posting['location_longitude']),
                                posting.get("location_bounds"),
                                posting.get("location_accuracy"))

                for level,loc in locs.items():
                    posting["location_" + level] = loc

            # If we were supplied a bounds array, convert it to a string for
            # storage.

            if "location_bounds" in posting:
                posting['location_bounds'] = repr(posting['location_bounds'])
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()

    # Get the Annotation objects used by these postings. Since these
    # objects hold unique annotation values, they can be shared across
    # postings -- we use the existing Annotation object if it exists, and
    # create new ones where necessary.

    annotations = {} # Maps annotation string to Annotation object.

    for src in parsed_postings:
        for annotation_value in src['annotations']:
            if annotation_value not in annotations:
                # The following attempts to work around a database deadlock
                # issue. We attempt to get_or_create the given Annotation
                # record, and if this results in a database deadlock, we wait a
                # moment before trying again.

                while True:
                    try:
                        annotation,created = Annotation.objects.get_or_create(
                                                annotation=annotation_value)
                    except DatabaseError,e:
                        if "deadlock" in str(e):
                            logger.debug("DEADLOCK DETECTED!!! TRYING AGAIN")
                            time.sleep(0.1)
                            continue
                        else:
                            raise
                    else:
                        break

                annotations[annotation_value] = annotation

    transaction.commit()

    # Save the postings into the database. Note that we simply process the
    # postings one at a time, using a transaction to periodically commit
    # changes. This may not be the fastest way to do it, but given the fact
    # that we have to update existing postings, we may not have a choice...

    try:
        num_postings_in_transaction = 0

        for src in parsed_postings:

            # Add or update the posting itself.

            src['posting']['inserted'] = dateHelpers.datetime_in_utc()

            posting,created = Posting.objects.get_or_create(
                                source_id=src['posting']['source_id'],
                                external_id=src['posting']['external_id'],
                                defaults=src['posting'])

            if not created:
                # We have an existing posting -> update it with the
                # newly-supplied values.
                for key,value in src['posting'].items():
                    if key not in ["source_id", "external_id"]:
                        setattr(posting, key, value)
                posting.save()

            # Add or update the posting's annotations.

            for annotation_value in src['annotations']:
                annotation = annotations[annotation_value]

                posting_annotation,created = \
                        PostingAnnotation.objects.get_or_create(
                                                posting=posting,
                                                annotation=annotation)

            # Add or update the posting's image references.

            existing_images = []
            for image_ref in ImageReference.objects.filter(posting=posting):
                existing_images.append(image_ref)

            for image in src['images']:
                full_url = image.get("full_url")
                thumbnail_url = image.get("thumbnail_url")

                already_exists = False
                for existing_image in existing_images:
                    if ((full_url == existing_image.full_url) and
                        (thumbnail_url == existing_image.thumbnail_url)):
                        already_exists = True
                        break

                if not already_exists:
                    image_ref = ImageReference()
                    image_ref.posting = posting
                    image_ref.full_url = full_url
                    image_ref.thumbnail_url = thumbnail_url
                    image_ref.save()

            # If we've created enough postings, commit the transaction.

            num_postings_in_transaction = num_postings_in_transaction + 1
            if num_postings_in_transaction >= MAX_NUM_POSTINGS_IN_TRANSACTION:
                transaction.commit()
                num_postings_in_transaction = 0

        # Now that the postings are in the database, send them out via the
        # notification system.

        # ...more to come!

        # That's all, folks!

        end_time = time.time()
        time_taken = int(1000 * (end_time - start_time))

        eventRecorder.record("POSTING_API", "POSTINGS_PROCESSED",
                             len(parsed_postings), time_taken)
    except:
        transaction.rollback()
        raise
    else:
        transaction.commit()

