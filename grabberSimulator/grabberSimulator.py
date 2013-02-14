""" grabberSimulator.py

    This program simulates the operation of an external grabber, sending
    posting data to the 3taps Posting API.

    Note that this program doesn't require PIP to be activated.  It does,
    however, require the following Python libraries:

        requests
        simplejson
        sqlite3
"""
import datetime
import os.path
import time
import urllib
import urllib2

import requests
import simplejson as json
import sqlite3 as sqlite

#############################################################################

POSTING_URL        = "http://127.0.0.1:5000/api/latest/posting/"
#POSTING_URL        = "http://data-commons.herokuapp.com/api/latest/posting/"
POSTING_CHUNK_SIZE = 10  # Number of postings to send off at once.

#############################################################################

def main():
    """ Our main program.
    """
    try:
        while True:
            wait_for = process_postings()
            if wait_for == None:
                break
            else:
                print "Waiting for %d seconds before trying again" % wait_for
                time.sleep(wait_for)
                continue
    except KeyboardInterrupt:
        pass

#############################################################################

def process_postings():
    """ Grab a bunch of postings and send them off to the Posting API.

        Upon completion, we return the "wait_for" value returned by the server,
        or None if the postings were not sent successfully.
    """
    start_time = time.time()

    next_posting_id = load_next_posting_id()

    postings = get_postings(next_posting_id)
    wait_for = send_postings_to_api(postings)
    if wait_for == None:
        # The postings didn't get through -> abandon ship.
        return None

    for id,posting in postings:
        if next_posting_id == None or id > next_posting_id:
            next_posting_id = id

    end_time = time.time()
    print "It took %0.4f seconds for the Posting API to process %d postings" \
        % (end_time - start_time, len(postings))

    if len(postings) > 0:
        save_next_posting_id(next_posting_id)
        return wait_for
    else:
        return None

#############################################################################

def load_next_posting_id():
    """ Load the "next-posting-id" value from disk.

        If we don't have a saved "next-posting-id" value, we return None.
    """
    if os.path.exists("next_posting_id.txt"):
        f = file("next_posting_id.txt", "r")
        s = f.read().strip()
        f.close()
        try:
            return int(s)
        except ValueError:
            return None
    else:
        return None

#############################################################################

def save_next_posting_id(next_posting_id):
    """ Save the "next-posting-id" value to disk.
    """
    f = file("next_posting_id.txt", "w")
    f.write(str(next_posting_id))
    f.close()

#############################################################################

def get_postings(next_posting_id):
    """ Retrieve the next 'POSTING_CHUNK_SIZE' postings from the database.

        Upon completion, we return a list of postings, where each list entry is
        an (id, posting) tuple.  'id' will be the record ID of this posting,
        and 'posting' will be a dictionary containing the postings's details.
    """
    connection = sqlite.connect("postings.db")
    cursor = connection.cursor()

    query = []
    query.append("SELECT id,raw_post FROM postings")
    if next_posting_id != None:
        query.append("WHERE id > %s" % next_posting_id)
    query.append("ORDER BY id")
    query.append("LIMIT %s" % POSTING_CHUNK_SIZE)
    query = " ".join(query)

    cursor.execute(query)

    results = []
    for row in cursor:
        id,raw_post = row

        posting = json.loads(raw_post)

        results.append((id, posting))

    return results

#############################################################################

def send_postings_to_api(raw_postings):
    """ Send the given list of postings to the 3taps Posting API.

        Upon completion, we return the 'wait_for' value returned by the server,
        or None if the postings were not sent successfully.
    """
    # Start by extracting the posting information we need from the raw
    # postings.

    def _copy(src_dict, src_key, dst_dict, dst_key):
        if src_dict.get(src_key) != None:
            dst_dict[dst_key] = src_dict[src_key]

    def _dateToSecs(date_str):
        """ Convert given timestamp string to number of seconds in unix time.
        """
        if date_str not in ["", None]:
            timestamp = datetime.datetime.strptime(date_str,
                                                   "%Y-%m-%dT%H:%M:%SZ")
            delta = timestamp - datetime.datetime(1970, 1, 1)
            return (delta.days*24*3600) + delta.seconds
        else:
            return None

    postings = []
    for id,raw_posting in raw_postings:
        posting = {}
        _copy(raw_posting, 'source',   posting, 'source')
        _copy(raw_posting, 'category', posting, 'category')

        location = {}
        if "location" in raw_posting:
            raw_location = raw_posting['location']
            _copy(raw_location, 'latitude',     location, 'lat')
            _copy(raw_location, 'longitude',    location, 'long')
            _copy(raw_location, 'accuracy',     location, 'accuracy')
            _copy(raw_location, 'countryCode',  location, 'country')
            _copy(raw_location, 'stateCode',    location, 'state')
            _copy(raw_location, 'metroCode',    location, 'metro')
            _copy(raw_location, 'regionCode',   location, 'region')
            _copy(raw_location, 'countyCode',   location, 'county')
            _copy(raw_location, 'cityCode',     location, 'city')
            _copy(raw_location, 'localityCode', location, 'locality')
            _copy(raw_location, 'zipCode',      location, 'zipcode')
        posting['location'] = location

        _copy(raw_posting, 'sourceId',  posting, 'external_id')
        _copy(raw_posting, 'sourceUrl', posting, 'external_url')
        _copy(raw_posting, 'heading',   posting, 'heading')
        _copy(raw_posting, 'body',      posting, 'body')
        _copy(raw_posting, 'html',      posting, 'html')

        if "postingTimestamp" in raw_posting:
            posting['timestamp'] = _dateToSecs(raw_posting['postingTimestamp'])
        if "expirationTimestamp" in raw_posting:
            posting['expires'] = _dateToSecs(raw_posting['expirationTimestamp'])

        _copy(raw_posting, 'language', posting, 'language')
        _copy(raw_posting, 'price',    posting, 'price')
        _copy(raw_posting, 'currency', posting, 'currency')

        images = []
        if "images" in raw_posting:
            for raw_image in raw_posting['images']:
                image = {}
                _copy(raw_image, 'thumbnail', image, 'thumbnail')
                _copy(raw_image, 'full',      image, 'full')
                if len(image) > 0:
                    images.append(image)
        posting['images'] = images

        annotations = {}
        if "annotations" in raw_posting:
            for key,value in raw_posting['annotations'].items():
                annotations[key] = value
        posting['annotations'] = annotations

        status = {}
        if "flags" in raw_posting:
            flags = raw_posting['flags']

            if flags & 1 == 1:
                status['offered'] = True
            elif flags & 2 == 2:
                status['lost'] = True
            elif flags % 4 == 4:
                status['stolen'] = True
            elif flags % 8 == 8:
                status['found'] = True
        posting['status'] = status

        _copy(raw_posting, 'immortal', posting, 'immortal')

        postings.append(posting)

    # Send the postings off to the Posting API.

    request = {'postings' : postings}

    print "Sending..."

    response = requests.post(POSTING_URL,
                             data=json.dumps(request),
                             headers={'content-type' : "application/json"})

    print "got response"

    if response.status_code != 200:
        print "Unexpected response:" + str(response.status_code)
        print
        print response.text
        return None

    if response.headers['content-type'] != "application/json":
        print "Server didn't return JSON data!"
        print
        print response.text
        return None

    response = response.json()

    # Check the response to see which postings failed (if any).

    num_sent = 0 # initially.
    if response != None:
        if "responses" in response:
            posting_errors = response['posting_errors']
            for i in range(len(posting_errors)):
                if posting_errors[i] != None:
                    for key in postings[i].keys():
                        print "  %s : %s" % (key, repr(postings[i][key]))
                    print "--> failed, reason = " + posting_errors[i]
                    print
                else:
                    num_sent = num_sent + 1

    return response.get("wait_for")

#############################################################################

if __name__ == "__main__":
    main()

