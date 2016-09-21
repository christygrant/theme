import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ast


from ckanext.spatial.interfaces import ISpatialHarvester

# Debug
import logging
import pprint
log = logging.getLogger(__name__)

ISO_NAMES = {'gmd': 'http://www.isotc211.org/2005/gmd',
             'xlink': 'http://www.w3.org/1999/xlink',
             'gco': 'http://www.isotc211.org/2005/gco',
             'gml': 'http://www.opengis.net/gml'}


def getRoleNames(xml_tree, roleString, roleNameElement):
    ''' Get names matching a specific ResponsibleParty role in a ISO XML document.
    '''
    roleNames = ''
    authorPathXML = './/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'
    for roleCode in xml_tree.xpath(authorPathXML, namespaces=ISO_NAMES):
        if roleCode.get('codeListValue') == roleString:
            newName = roleCode.getparent().getparent().findtext(roleNameElement, namespaces=ISO_NAMES)
            log.debug('role ' + roleString + ':  newName == "' + newName + '"')
            if newName: 
                roleNames += newName + "|"

    if len(roleNames) > 0:
        roleNames = roleNames[0:-1]
    else:
        roleNames = ' '
    return roleNames


def getDataCiteResourceTypes(xml_tree):
    ''' Add resource type fields by searching the ISO XML for keywords with thesaurus containing "DataCite". 
    '''
    thesaurusPath = './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName'
    keywordPath = './/gmd:keyword/gco:CharacterString'
    resourceTypes = ''
    for thesaurus in xml_tree.xpath(thesaurusPath, namespaces=ISO_NAMES):
        if "DataCite" in thesaurus.findtext('gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces=ISO_NAMES):
            md_keywords = thesaurus.getparent()
            for keyword in md_keywords.xpath(keywordPath, namespaces=ISO_NAMES):
                newResourceType = keyword.text
                log.debug('newResourceType == "' + newResourceType + '"')
                if newResourceType:
                    resourceTypes += newResourceType + "|"

    if len(resourceTypes) > 0:
        resourceTypes = resourceTypes[0:-1]
    else:
        resourceTypes = ' '
    return resourceTypes


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
	
        # Add author field
	authorString = getRoleNames(xml_tree, 'author', 'gmd:individualName/gco:CharacterString')
        package_dict['extras'].append({'key': 'author1', 'value': authorString})

        # Examine iso_values if there are authors, just to get a better idea of harvester behavior.
	if len(authorString) > 1:
            log.debug("START iso_values print:")
            log.debug(pprint.pformat(iso_values))
            log.debug("END iso_values print.")
	
        # Add publisher field
	publisherString = getRoleNames(xml_tree, 'publisher', 'gmd:organisationName/gco:CharacterString')
        package_dict['extras'].append({'key': 'publisher', 'value': publisherString})
	
        # Add DataCite Resource Type field
	resourceTypeString = getDataCiteResourceTypes(xml_tree)
        package_dict['extras'].append({'key': 'datacite-resource-type', 'value': resourceTypeString})
	
        # Add Harvest Object Id
	harvest_object_id = data_dict['harvest_object'].id
        package_dict['extras'].append({'key': 'harvest_object_id', 'value': harvest_object_id})
	
        log.debug("START data_dict print:")
        log.debug(pprint.pformat(data_dict))
        log.debug("END data_dict print.")
        return package_dict

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dset_harvester')

