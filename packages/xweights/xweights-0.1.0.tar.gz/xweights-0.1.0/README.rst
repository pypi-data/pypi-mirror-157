========
xweights
========

.. image:: https://github.com/ludwiglierhammer/xweights/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/ludwiglierhammer/xweights/actions/workflows/ci.yml
    
.. image:: https://codecov.io/gh/ludwiglierhammer/xweights/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/ludwiglierhammer/xweights
    
.. image:: https://readthedocs.org/projects/xweights/badge/?version=latest
    :target: https://xweights.readthedocs.io/en/latest/?version=latest
    :alt: Documentation Status  
        
.. image:: https://pyup.io/repos/github/ludwiglierhammer/xweights/shield.svg
    :target: https://pyup.io/repos/github/ludwiglierhammer/xweights/
    :alt: Updates   

Python "xweights" contains all the functions to calculate grid weighted area means from predefined regions or from an user-given shapefile. This tool is a wrapper around the python package xesmf https://xesmf.readthedocs.io

* Free software: MIT license
* Documentation: https://xweights.readthedocs.io


Features
--------

* Calculate grid-weighted-means and save the output as CSV file

* As input you can choose between files on disk and intake-esm catalogues. Xarray dataset input is under development.

* Use all these features as an command-line tool too


Installation
------------

You can install the package directly from github using pip:

.. code-block:: console

     pip install git+https://github.com/ludwiglierhammer/xweights

If you want to contribute, I recommend cloning the repository and installing the package in development mode, e.g.

.. code-block:: console

    git clone https://github.com/ludwiglierhammer/xweights.git
    cd xweights
    pip install -e .

In additon you have to install xESMF using _Conda:

.. code-block:: console
		
    conda install -c conda-forge xesmf
    
This will install the package but you can still edit it and you don't need the package in your :code:`PYTHONPATH`


Requirements
------------

* python3.6 or higher

* numpy

* pandas

* geopandas

* intake-esm

* xarray 

* py-cordex

* xesmf


Contact
-------
In cases of any problems, needs or wishes do not hesitate to contact:

ludwig.lierhammer@hereon.de


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Conda: https://docs.conda.io/
