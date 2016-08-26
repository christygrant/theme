import ckan.plugins as p
import ckan.plugins.toolkit as toolkit


from ckanext.spatial.interfaces import ISpatialHarvester

# Debug
import logging
from pprint import pprint

log = logging.getLogger(__name__)

ISO_NAMES = {'gmd': 'http://www.isotc211.org/2005/gmd',
             'xlink': 'http://www.w3.org/1999/xlink',
             'gco': 'http://www.isotc211.org/2005/gco',
             'gml': 'http://www.opengis.net/gml'}

class Dset_HarvesterPlugin(p.SingletonPlugin):
    p.implements(ISpatialHarvester, inherit=True)
    p.implements(p.IConfigurer)

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
	authorList = []
        authorPathXML = './/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty'
        for party in xml_tree.xpath(authorPathXML, namespaces=ISO_NAMES):
	    roleString = party.findtext('gmd:role/gmd:CI_RoleCode', namespaces=ISO_NAMES)
            log.debug('roleString == "' + roleString + '"')
            if roleString == 'author':
	        authorList.append(party.findtext('gmd:individualName/gco:CharacterString', namespaces=ISO_NAMES))
	
        package_dict['author'] = authorList

        return package_dict

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dset_harvester')


