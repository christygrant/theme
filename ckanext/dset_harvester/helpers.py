import ckan.lib.helpers as h
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import json


DSET_DATE_FORMAT='%B %d, %Y, %I:%M %p'

# Debug
import logging
import pprint
log = logging.getLogger(__name__)

def string_to_json(json_string):
    '''  Converts a string representation of a JSON object into that object
    '''
    if json_string:
        json_data = json.loads(json_string)
    else: 
        json_data = ['Missing!']
    return json_data


def dset_index(extras_tuple):
    ''' Used for sorting 'extras' : function returns a sorting index for a given (key, value) tuple.
        If the key is not in the list, it is given an index larger than any in the ordering list.
    '''
    displayOrdering = ["Resource Type", "Author", "Publication Date", "Metadata Date", "Publisher",
                       "Resource Support Contact", "Metadata Support Contact", 
                       "Topic Category", 
                       "Temporal Extent Begin", "Temporal Extent End", 
                       "Bbox North Lat", "Bbox South Lat", "Bbox West Long", "Bbox East Long"] 
    missingKeyIndex = len(displayOrdering) 

    key = extras_tuple[0]
    if key in displayOrdering:
         keyIndex = displayOrdering.index(key)
    else:
         keyIndex = missingKeyIndex
    return keyIndex


def dset_sorted_extras(extras):
    return sorted(extras, key=dset_index)

def dset_render_datetime(datetime_, date_format=DSET_DATE_FORMAT, with_hours=True):
    '''Render a datetime object or timestamp string as a localised date or
    in the requested format.
    If timestamp is badly formatted, then THE ORIGINAL string is returned.
    Also, default date_format to our preferred format (e.g. September 30, 2000, 08:00 PM)
    '''
    rendered_datetime = h.render_datetime(datetime_, date_format, with_hours)
    log.debug("IN NEW HELPER rendered_datetime = " + rendered_datetime)
    if not rendered_datetime:
        return datetime_
    else:
        return rendered_datetime

def dset_valid_temporal_extent (begin, end):
    '''Check if both start and end dates are valid dates
       Try to render (doesn't need format to check if it can convert string.  The h.render_datetime returns '' if it can't convert to datetime)
    '''
    valid=False
    if h.render_datetime(begin):
        if h.render_datetime(end):
            valid=True
    # If one of these is NoneType will cause Server Error so don't check in with this on.
    # log.debug ("The Temporal extent " + begin + "-" + end + " is " + str(valid))
    return valid
    

