===========
nxsfileinfo
===========

Description
-----------

The nxsfileinfo program show metadata from nexus files

Synopsis
--------

.. code:: bash

	  nxsfileinfo <command> [options] <nexus_file_name>


The following commands are available: general, field


nxsfileinfo general
-------------------

It shows general information for he nexus file.

Synopsis
""""""""

.. code:: bash

	  nxsfileinfo general <nexus_file_name>

Options:
  -h, --help            show this help message and exit
  --h5py                use h5py module as a nexus reader
  --h5cpp               use h5cpp module as a nexus reader

Example
"""""""

.. code:: bash

	  nxsfileinfo general saxs_ref1_02.nxs

nxsfileinfo field
-----------------

It shows field information for the nexus file.

Synopsis
""""""""

.. code:: bash

	  Usage: nxsfileinfo field <file_name>

Options:
   -h, --help            show this help message and exit
   -c HEADERS, --columns=HEADERS
       names of column to be shown (separated by commas without spaces). The possible names are: depends_on, dtype, full_path, nexus_path, nexus_type, shape, source, source_name, source_type, strategy, trans_type, trans_offset, trans_vector, units, value
   -f FILTERS, --filters=FILTERS
       full_path filters (separated by commas without spaces). Default: '*'. E.g. '*:NXsample/*'
   -v VALUES, --values=VALUES
       field names which value should be stored (separated by commas without spaces). Default: depends_on
   -g, --geometry        show fields with geometry full_path filters, i.e. *:NXtransformations/*,*/depends_on. It works only when -f is not defined
   -s, --source          show datasource parameters
   --h5py                use h5py module as a nexus reader
   --h5cpp               use h5cpp module as a nexus reader


Example
"""""""

.. code:: bash

	  nxsfileinfo field /tmp/saxs_ref1_02.nxs
          nxsfileinfo field /user/data/myfile.nxs -g
          nxsfileinfo field /user/data/myfile.nxs -s

nxsfileinfo metadata
--------------------

It shows metadata of the nexus file.

Synopsis
""""""""

.. code:: bash

	  Usage: nxsfileinfo metadata <file_name>

Options:
   -h, --help            show this help message and exit
   -a ATTRS, --attributes ATTRS
                        names of field or group attributes to be show (separated by commas without spaces). The default takes all attributes
   -n NATTRS, --hidden-attributes NATTRS
                        names of field or group attributes to be hidden (separated by commas without spaces). The default: 'nexdatas_source,nexdatas_strategy'
   -v VALUES, --values VALUES
                        field names of more dimensional datasets which value should be shown (separated by commas without spaces)
   -g GROUP_POSTFIX, --group-postfix GROUP_POSTFIX
                        postfix to be added to NeXus group name. The default: 'Parameters'
   -t ENTRYCLASSES, --entry-classes ENTRYCLASSES
                        names of entry NX_class to be shown (separated by commas without spaces). If name is '' all groups are shown. The default: 'NXentry'
   -e ENTRYNAMES, --entry-names ENTRYNAMES
                        names of entry groups to be shown (separated by commas without spaces). If name is '' all groups are shown. The default: ''
   -r, --raw-metadata    do not store NXentry as scientificMetadata
   -p PID, --pid PID
                        dataset pid
   -i BEAMTIMEID, --beamtimeid BEAMTIMEID
                        beamtime id
   -u, --pid-with-uuid
                        generate pid with uuid
   -f, --pid-with-filename
                        generate pid with file name
   -b BEAMTIMEMETA, --beamtime-meta BEAMTIMEMETA
                        beamtime metadata file
   -s SCIENTIFICMETA, --scientific-meta SCIENTIFICMETA
                        scientific metadata file
   -o OUTPUT, --output OUTPUT
                        output scicat metadata file
   --h5py               use h5py module as a nexus reader
   --h5cpp              use h5cpp module as a nexus reader

Example
"""""""

.. code:: bash

          nxsfileinfo metadata /user/data/myfile.nxs
          nxsfileinfo metadata /user/data/myfile.nxs -p 'Group'
          nxsfileinfo metadata /user/data/myfile.nxs -s
          nxsfileinfo metadata /user/data/myfile.nxs -a units,NX_class
