import ckan.lib.helpers as h
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import json

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


def get_publication_date(package):
    '''  Searches a list of dictionaries and returns the date associated with a publication. 

         Example Input:  u'[{"type": "creation", "value": "2015-01-06"},
                            {"type": "publication", "value": "2015-02-05"}]'
         Returns:        "2015-02-05"
    '''
    data_string = h.get_pkg_dict_extra(package, 'dataset-reference-date')
    data_list = json.loads(data_string)
    log.debug("Data_list type = " + str(type(data_list)))
    pub_date = 'Not Found'
    for date_dict in data_list:
        log.debug(pprint.pformat(date_dict))
        if date_dict['type'] == 'publication':
	    pub_date = date_dict['value']
    return pub_date


def dset_index(extras_tuple):
    ''' Used for sorting 'extras' : function returns a sorting index for a given (key, value) tuple.
        If the key is not in the list, it is given an index larger than any in the ordering list.
    '''
    displayOrdering = ["Resource Type", "Author", "Publication Date", "Metadata Date", "Publisher",
                       "Resource Support Contact", "Metadata Support Contact", 
                       "Topic Category", 
                       "Temporal Extent Begin", "Temporal Extent End", 
                       "Bbox North Lat", "Bbox South Lat", "Bbox West Long", "Bbox East Long", 
                       "Publisher"] 
    missingKeyIndex = len(displayOrdering) 

    key = extras_tuple[0]

    if key in displayOrdering:
         keyIndex = displayOrdering.index(key)
    else:
         keyIndex = missingKeyIndex

    return keyIndex


def dset_sorted_extras(extras):
    return sorted(extras, key=dset_index)
