import ckan.lib.helpers as h
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import json

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
    pub_date = 'Not Found'
    for date_dict in data_list:
        if date_dict['type'] == 'publication':
	    pub_date = date_dict['value']
    return pub_date

