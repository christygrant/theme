import ckan.lib.helpers as h
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import json
import dateutil.parser


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


def dset_render_datetime(dateTimeString):
    '''Render a timestamp string using a preferred format (e.g. September 30, 2000, 08:00 PM)
       If timestamp is badly formatted, then THE ORIGINAL string is returned.
    '''
    dateFormat = '%B %d, %Y, %I:%M %p'
    try:
        dateTimeObject = dateutil.parser.parse(dateTimeString, ignoretz=True)
        renderedDateTime = h.render_datetime(dateTimeObject, dateFormat, True)
    except ValueError:
        renderedDateTime = dateTimeString
    return renderedDateTime


def dset_valid_temporal_extent (begin, end):
    '''Check if both start and end dates are valid dates
    '''
    if begin and end:
        try:
            dateTimeObject = dateutil.parser.parse(begin, ignoretz=True)
            dateTimeObject = dateutil.parser.parse(end, ignoretz=True)
            valid=True
        except ValueError:
            valid=False
    else:
        valid = False
    return valid
    

