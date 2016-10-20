
=============
ckanext-dset_harvester
=============

This plugin adds additional behavior to the CKAN spatial harvester.  It extracts additional information from ISO-19139 documents that matches meets the needs for searching NCAR digital assets.

------------
Requirements
------------

This extension requires both the CKAN "harvest" and "spatial" plugins.   It has been tested with "spatial" version 0.1 and "harvest" version 0.0.5, using a base CKAN version 2.4.1.


------------
Installation
------------

To install ckanext-dset_harvester for development, activate your CKAN virtualenv and
do::

    cd /usr/lib/ckan/default/src
    git clone https://github.com/bonnland/ckanext-dset_harvester.git
    cd ckanext-dset_harvester
    python setup.py develop


Then add ``dset_harvester`` to the ``ckan.plugins`` setting in your CKAN
   config file (``/etc/ckan/default/development.ini``).

Then restart the harvesting queues. If you're running the queues using the "supervisor" service::

     sudo systemctl restart supervisord

You will have to re-harvest datasets in order to have the additional dataset attributes added or updated.
