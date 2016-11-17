import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ast
import json


from ckanext.spatial.interfaces import ISpatialHarvester
import ckanext.dset_harvester.helpers as helpers


# Debug
import logging
import pprint
log = logging.getLogger(__name__)

ISO_NAMES = {'gmd': 'http://www.isotc211.org/2005/gmd',
             'xlink': 'http://www.w3.org/1999/xlink',
             'gco': 'http://www.isotc211.org/2005/gco',
             'gml': 'http://www.opengis.net/gml'}


def getNamesByRole(xml_tree, roleString, roleNameElement):
    ''' Get names matching a specific ResponsibleParty role in a ISO XML document.
    '''
    roleNames = []
    rolePathXML = './/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode'
    for roleCode in xml_tree.xpath(rolePathXML, namespaces=ISO_NAMES):
        if roleCode.get('codeListValue') == roleString:
            newName = roleCode.getparent().getparent().findtext(roleNameElement, namespaces=ISO_NAMES)
            if newName: 
                log.debug('role ' + roleString + ':  newName == "' + newName + '"')
                roleNames.append(newName)

    if len(roleNames) == 0:
        roleNames = [' ']
    return roleNames


def getDataCiteResourceTypes(xml_tree):
    ''' Add resource type fields by searching the ISO XML for keywords with thesaurus containing "DataCite". 
    '''
    thesaurusPath = './/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:thesaurusName'
    keywordPath = './/gmd:keyword/gco:CharacterString'
    resourceTypes = []
    for thesaurus in xml_tree.xpath(thesaurusPath, namespaces=ISO_NAMES):
        if "DataCite" in thesaurus.findtext('gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces=ISO_NAMES):
            md_keywords = thesaurus.getparent()
            for keyword in md_keywords.xpath(keywordPath, namespaces=ISO_NAMES):
                newResourceType = keyword.text
                if newResourceType:
                    log.debug('newResourceType == "' + newResourceType + '"')
                    resourceTypes.append(newResourceType)

    if len(resourceTypes) == 0:
        resourceTypes = [' ']
    return resourceTypes

def getSupportContactName(xml_tree, contactPath):
    supportContactElementList = xml_tree.xpath(contactPath, namespaces=ISO_NAMES)
    if supportContactElementList:
        supportContactElement = supportContactElementList[0]

        individualElementList = supportContactElement.xpath('.//gmd:individualName/gco:CharacterString', namespaces=ISO_NAMES)
        individualNameString = ""
        if individualElementList:
            individualNameString = individualElementList[0].text
   
    return individualNameString

def getSupportContactOrg(xml_tree, contactPath):
    supportContactElementList = xml_tree.xpath(contactPath, namespaces=ISO_NAMES)
    if supportContactElementList:
        supportContactElement = supportContactElementList[0]

        orgElementList = supportContactElement.xpath('.//gmd:organisationName/gco:CharacterString', namespaces=ISO_NAMES)
        orgString = ""
        if orgElementList:
            orgString = orgElementList[0].text

    return orgString


def getSupportContactEmail(xml_tree, contactPath):
    supportContactElementList = xml_tree.xpath(contactPath, namespaces=ISO_NAMES)
    if supportContactElementList:
        supportContactElement = supportContactElementList[0]

        emailString = ""
        emailElementList = supportContactElement.xpath('.//gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString', namespaces=ISO_NAMES)
        if emailElementList:
            emailString = emailElementList[0].text
	
    return emailString


def getPublicationDate(dataset_reference_date):
    publication_date = " "
    for date_dict in dataset_reference_date:
        if date_dict['type'] == 'publication':
            publication_date = date_dict['value']
    return publication_date


def getSplitKeywordsGCMD(harvested_keywords):
    ''' convert something like
        "EARTH    SCIENCE > ATMOSPHERE > ATMOSPHERIC    ELECTRICITY > ATMOSPHERIC CONDUCTIVITY"
        into
        ['earth science', 'atmosphere', 'atmospheric electricity', 'atmospheric conductivity']
    '''
    split_keywords = []
    for k in harvested_keywords:
        kk = k.split('>')
        kk = [k.lower().strip() for k in kk]
        kk = [' '.join(k.split()) for k in kk]
        split_keywords.extend(kk)
    split_keywords = list(set(split_keywords))
    return split_keywords



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
	
        # Add author field
	authorList = getNamesByRole(xml_tree, 'author', 'gmd:individualName/gco:CharacterString')
        authorString = json.dumps(authorList)
        package_dict['extras'].append(
            {'key': 'harvest-author', 'value': authorString}
        )

        # Examine iso_values if there are authors, just to get a better idea of harvester data structures.
	if len(authorString) > 1:
            log.debug("START iso_values print:")
            log.debug(pprint.pformat(iso_values))
            log.debug("END iso_values print.")
	
        # Add publisher field
	publisherList = getNamesByRole(xml_tree, 'publisher', 'gmd:organisationName/gco:CharacterString')
        publisherString = json.dumps(publisherList)
        package_dict['extras'].append({'key': 'publisher', 'value': publisherString})
	
        # Add Support Contact fields
        # TODO: Resource Support Contact Object?

        resourceSupportIsoPath = './/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty'
        resourceSupportName = getSupportContactName(xml_tree, resourceSupportIsoPath)
        package_dict['extras'].append({'key': 'resource-support-name', 'value': resourceSupportName})

        resourceSupportOrg = getSupportContactOrg(xml_tree, resourceSupportIsoPath)
        package_dict['extras'].append({'key': 'resource-support-org', 'value': resourceSupportOrg})

        resourceSupportEmail = getSupportContactEmail(xml_tree, resourceSupportIsoPath)
        package_dict['extras'].append({'key': 'resource-support-email', 'value': resourceSupportEmail})

        # Metadata point of contact
	# TODO: don't build string here. Esp check for null org.
        pointOfContactIsoPath = './/gmd:contact/gmd:CI_ResponsibleParty'
        pointOfContactName = getSupportContactName(xml_tree, pointOfContactIsoPath)
        pointOfContactOrg = getSupportContactName(xml_tree, pointOfContactIsoPath)
        pointOfContactString = pointOfContactName + "(" + pointOfContactOrg + ")"
        package_dict['extras'].append({'key': 'metadata-point-of-contact', 'value': pointOfContactString})

        # Set CKAN Resource Type to first DataCite ResourceType keyword (CKAN only allows one keyword)
	resourceTypeList = getDataCiteResourceTypes(xml_tree)
        for extra in package_dict['extras']:
            if extra['key'] == 'resource-type':
                extra['value'] = resourceTypeList[0]
	
        # Add Harvester-related values
        harvest_object = data_dict['harvest_object']
        package_dict['extras'].append({'key': 'harvested_object_id', 'value': harvest_object.id})
        package_dict['extras'].append({'key': 'harvester_source_id', 'value': harvest_object.harvest_source_id})
        package_dict['extras'].append({'key': 'harvester_source_title', 'value': harvest_object.source.title})

        # Add Publication Date field
        publication_date = getPublicationDate(iso_values['dataset-reference-date'])
        package_dict['extras'].append({'key': 'publication-date', 'value': publication_date})

        # Convert GCMD Keywords to split form
        splitKeywords = getSplitKeywordsGCMD(iso_values.pop('tags'))
        package_dict['tags'] = [{'name': t} for t in splitKeywords]

        # Convert some harvested fields from lists to JSON (spatial harvester is inconsistent in its output)
        for key in ('topic-category','access-constraints'):
           for extra in package_dict['extras']:
               if extra['key'] == key:
                   extra['value'] = json.dumps(extra['value'])
	
        #log.debug("START data_dict print:")
        #log.debug(pprint.pformat(data_dict))
        #log.debug("END data_dict print.")
        return package_dict

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dset_harvester')

   # ITemplateHelpers

    def get_helpers(self):

        function_names = (
            'string_to_json',
            'dset_sorted_extras',
        )
        return _get_module_functions(helpers, function_names)



def _get_module_functions(module, function_names):
    functions = {}
    for f in function_names:
        functions[f] = module.__dict__[f]

    return functions
