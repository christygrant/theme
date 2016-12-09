import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from collections import OrderedDict

# Debug
import logging
import pprint
log = logging.getLogger(__name__)


def getCustomFacets(facets_dict):
    '''  Customize facets on dataset search page and organization page.
    '''
    #log.debug("facets_dict:")
    #log.debug(pprint.pformat(facets_dict))

    # Remove facet "groups"
    if 'groups' in facets_dict:
        del facets_dict['groups']

    # Remove facet "license_id"
    if 'license_id' in facets_dict:
        del facets_dict['license_id']

    # Add facet "Resource Type" 
    facets_dict['resource-type'] = plugins.toolkit._('Resource Type')

    # Move Formats facet to the end. 
    if 'res_format' in facets_dict:
        del facets_dict['res_format']
        facets_dict['res_format'] = plugins.toolkit._('Formats')

    return facets_dict


class Custom_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'custom_theme')

    ##  IFacets 

    def dataset_facets(self, facets_dict, package_type):
        custom_facets_dict = getCustomFacets(facets_dict)
        return custom_facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        custom_facets_dict = getCustomFacets(facets_dict)
        return custom_facets_dict
