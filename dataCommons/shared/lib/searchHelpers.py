""" dataCommons.shared.lib.searchHelpers

    This module defines various helper functions for performing searches
    against the posting database.
"""
import logging

from dataCommons.shared.models import *
from django.db.models          import Q
from dataCommons.shared.lib    import dateHelpers, annotationParser

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def add_heading_search(query, text):
    """ Filter a SearchQuery to find the given text in the posting's heading.

        'query' is a SearchQuery that filters records in the Posting table, and
        'text' is a string to search for.

        We return a new SearchQuery with an appropriate extra() clause added
        that performs a full-text search against the posting's heading field.
    """
    return query.extra(where=["(heading_tsv @@ plainto_tsquery(%s))"],
                       params=[text])

#############################################################################

def add_body_search(query, text):
    """ Filter a SearchQuery to find the given text in the posting's body.

        'query' is a SearchQuery that filters records in the Posting table, and
        'text' is a string to search for.

        We return a new SearchQuery with an appropriate extra() clause added
        that performs a full-text search against the posting's body field.
    """
    return query.extra(where=["(body_tsv @@ plainto_tsquery(%s))"],
                       params=[text])

#############################################################################

def add_heading_or_body_search(query, text):
    """ Filter SearchQuery to find some text in the posting's heading or body.

        'query' is a SearchQuery that filters records in the Posting table, and
        'text' is a string to search for.

        We return a new SearchQuery with an appropriate extra() clause added
        that performs a full-text search against the posting's heading and body
        fields.
    """
    return query.extra(where=["((heading_tsv @@ plainto_tsquery(%s)) OR " +
                              "(body_tsv @@ plainto_tsquery(%s)))"],
                       params=[text, text])

#############################################################################

def build_search_query(criteria):
    """ Build and return a QuerySet object based on the given search criteria.

        We construct a search query that will search against the given set of
        search criteria.

        Upon completion, we return a (success, result) tuple, where 'success'
        is True if and only if we could build a search query out of the given
        search criteria.  If 'success' is True, 'result' will be the QuerySet
        object we created.  Otherwise, 'result' will be a string explaining why
        we couldn't construct the query set.
    """
    query = Posting.objects.all() # initially.

    # Append locations filters.

    if "country" in criteria:
        try:
            country = Location.objects.get(code=criteria['country'],
                                           level=Location.LEVEL_COUNTRY)
        except Location.DoesNotExist:
            return (False, "Unknown country: " + criteria['country'])
        query = query.filter(location_country=country)

    if "state" in criteria:
        try:
            state = Location.objects.get(code=criteria['state'],
                                         level=Location.LEVEL_STATE)
        except Location.DoesNotExist:
            return (False, "Unknown state: " + criteria['state'])
        query = query.filter(location_state=state)

    if "metro" in criteria:
        try:
            metro = Location.objects.get(code=criteria['metro'],
                                         level=Location.LEVEL_METRO)
        except Location.DoesNotExist:
            return (False, "Unknown metro: " + criteria['metro'])
        query = query.filter(location_metro=metro)

    if "region" in criteria:
        try:
            region = Location.objects.get(code=criteria['region'],
                                          level=Location.LEVEL_REGION)
        except Location.DoesNotExist:
            return (False, "Unknown region: " + criteria['region'])
        query = query.filter(location_region=region)

    if "county" in criteria:
        try:
            county = Location.objects.get(code=criteria['county'],
                                          level=Location.LEVEL_COUNTY)
        except Location.DoesNotExist:
            return (False, "Unknown county: " + criteria['county'])
        query = query.filter(location_county=county)

    if "city" in criteria:
        try:
            city = Location.objects.get(code=criteria['city'],
                                        level=Location.LEVEL_CITY)
        except Location.DoesNotExist:
            return (False, "Unknown city: " + criteria['city'])
        query = query.filter(location_city=city)

    if "locality" in criteria:
        try:
            locality = Location.objects.get(code=criteria['locality'],
                                            level=Location.LEVEL_LOCALITY)
        except Location.DoesNotExist:
            return (False, "Unknown locality: " + criteria['locality'])
        query = query.filter(location_locality=locality)

    if "zipcode" in criteria:
        try:
            zipcode = Location.objects.get(code=criteria['zipcode'],
                                           level=Location.LEVEL_ZIPCODE)
        except Location.DoesNotExist:
            return (False, "Unknown zipcode: " + criteria['zipcode'])
        query = query.filter(location_zipcode=zipcode)

    # Append other filters.

    if "category_group" in criteria:
        try:
            group = CategoryGroup.objects.get(code=criteria['category_group'])
        except CategoryGroup.DoesNotExist:
            return (False,
                    "Unknown category group: " + criteria['category_group'])
        query = query.filter(category_group=group)

    if "category" in criteria:
        try:
            category = Category.objects.get(code=criteria['category'])
        except Category.DoesNotExist:
            return (False, "Unknown category: " + criteria['category'])
        query = query.filter(category=category)

    if "source" in criteria:
        try:
            source = Source.objects.get(code=criteria['source'])
        except Source.DoesNotExist:
            return (False, "Unknown source: " + criteria['source'])
        query = query.filter(source=source)

    if "external_id" in criteria:
        query = query.filter(external_id=criteria['external_id'])

    if "heading" in criteria:
        query = add_heading_search(query, criteria['heading'])

    if "body" in criteria:
        query = add_body_search(query, criteria['body'])

    if "text" in criteria:
        query = add_heading_or_body_search(query, criteria['text'])

    if "timestamp" in criteria:
        if ".." not in criteria['timestamp']:
            return (False,
                    "Invalid timestamp criteria: " + criteria['timestamp'])
        s1,s2 = criteria['timestamp'].split("..", 1)
        try:
            min_timestamp = int(s1)
        except ValueError:
            return (False, "Invalid timestamp value: " + s1)
        try:
            max_timestamp = int(s2)
        except ValueError:
            return (False, "Invalid timestamp value: " + s2)
        min_timestamp = dateHelpers.datetime_in_utc(min_timestamp)
        max_timestamp = dateHelpers.datetime_in_utc(max_timestamp)
        query = query.filter(timestamp__gte=min_timestamp,
                             timestamp__lte=max_timestamp)

    if "price" in criteria:
        if ".." not in criteria['price']:
            return (False, "Invalid price criteria: " + criteria['price'])
        s1,s2 = criteria['price'].split("..", 1)
        if s1 != "":
            try:
                min_price = float(s1)
            except ValueError:
                return (False, "Invalid price value: " + s1)
            query = query.filter(price__gte=min_price)
        if s2 != "":
            try:
                max_price = float(s2)
            except ValueError:
                return (False, "Invalid price value: " + s2)
            query = query.filter(price__lte=max_price)

    if "id" in criteria:
        if ".." in criteria['id']:
            s1,s2 = criteria['id'].split("..", 1)
            try:
                min_id = int(s1)
            except ValueError:
                return (False, "Invalid id value: " + s1)
            try:
                max_id = int(s2)
            except ValueError:
                return (False, "Invalid id value: " + s2)
            query = query.filter(id__gte=min_id, id__lte=max_id)
        else:
            try:
                id = int(criteria['id'])
            except ValueError:
                return (False, "Invalid id value: " + criteria['id'])
            query = query.filter(id=id)

    if "currency" in criteria:
        query = query.filter(currency=criteria['currency'])

    if "annotations" in criteria:
        success,result = annotationParser.parse(criteria['annotations'])
        if not success:
            return (False, result)
        else:
            query = query.filter(result)

    if "status" in criteria:
        if criteria['status'] == "offered":
            query = query.filter(status_offered=True)
        if criteria['status'] == "wanted":
            query = query.filter(status_wanted=True)
        elif criteria['status'] == "lost":
            query = query.filter(status_lost=True)
        elif criteria['status'] == "stolen":
            query = query.filter(status_stolen=True)
        elif criteria['status'] == "found":
            query = query.filter(status_found=True)
        elif criteria['status'] == "deleted":
            query = query.filter(status_deleted=True)
        else:
            return (False, "Invalid status criteria: " + criteria['status'])

    if "has_image" in criteria:
        if criteria['has_image'] == "1":
            query = query.filter(has_image=True)
        elif criteria['has_image'] == "0":
            query = query.filter(has_image=False)
        else:
            return (False,
                    "Invalid has_image criteria: " + criteria['has_image'])

    include_deleted = False # initially.
    only_deleted    = False

    if "include_deleted" in criteria:
        if criteria['include_deleted'] == "1":
            include_deleted = True

    if "only_deleted" in criteria:
        if criteria['only_deleted'] == "1":
            only_deleted = True

    if not include_deleted and not only_deleted:
        query = query.filter(status_deleted=False)
    elif only_deleted:
        query = query.filter(status_deleted=True)

    return (True, query)

