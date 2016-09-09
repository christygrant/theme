import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ast


from ckanext.spatial.interfaces import ISpatialHarvester

# Debug
import logging
from pprint import pprint
log = logging.getLogger(__name__)


def str_undo(listString):
    ''' This helper function converts a string version of a list back to a list.  
    In other words: str_undo(str(list)) == list .
    '''
    log.debug("str_undo():  length of listString is " + str(len(listString)))
    if isinstance(listString, basestring):
        log.debug("str_undo():  listString  == " + listString)
        convertedList = ast.literal_eval(listString)
    else:
        convertedList = listString
    log.debug("str_undo():  length of list is " + str(len(convertedList)))
    return convertedList


ISO_NAMES = {'gmd': 'http://www.isotc211.org/2005/gmd',
             'xlink': 'http://www.w3.org/1999/xlink',
             'gco': 'http://www.isotc211.org/2005/gco',
             'gml': 'http://www.opengis.net/gml'}

class Dset_HarvesterPlugin(p.SingletonPlugin):
    p.implements(ISpatialHarvester, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    # ISpatialHarvester

    def get_package_dict(self, context, data_dict):
        package_dict = data_dict['package_dict']
        iso_values = data_dict['iso_values']
        xml_tree = data_dict['xml_tree']

        # Add ISO Topic Category from spatial harvester 
        package_dict['extras'].append(
            {'key': 'topic-category', 'value': iso_values.get('topic-category')}
        )
	
        # Add Authors by searching the ISO XML for "cited responsible parties" with an "author" role. 
	authorString = ''
        authorPathXML = './/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty'
        for party in xml_tree.xpath(authorPathXML, namespaces=ISO_NAMES):
	    roleString = party.findtext('gmd:role/gmd:CI_RoleCode', namespaces=ISO_NAMES)
            log.debug('roleString == "' + roleString + '"')
            if roleString.lower() == 'author':
	        authorString += party.findtext('gmd:individualName/gco:CharacterString', namespaces=ISO_NAMES)
	        authorString += '|'

        if len(authorString) > 0:
            package_dict['extras'].append(
                {'key': 'author1', 'value': authorString[0:-1]}
            )
        else:
            package_dict['extras'].append(
                {'key': 'author1', 'value': ' '}
            )
	
        return package_dict

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dset_harvester')


    # ITemplateHelpers
    def get_helpers(self):
        ''' Register str_undo() as a template helper function.
        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'dset_harvester_str_undo': str_undo}
