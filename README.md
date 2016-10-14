# ckanext-custom_theme
CKAN extension for applying theme more consistent with NCAR's.
Clone this into /usr/lib/ckan/default/src

After cloning, run this in the ckanext-custom_theme directory to register the extension:
python setup.py develop

Add custom_theme to ckan.plugins list in your /etc/ckan/default/ .ini file

Edit .ini file to put in theme settings::

    ## Front-End Settings
    ckan.site_title = NCAR DSET Search
    ckan.site_logo = /ncar_header.png
    ckan.site_description = NCAR data search and discovery
    ckan.favicon = /NCARfavicon.ico
