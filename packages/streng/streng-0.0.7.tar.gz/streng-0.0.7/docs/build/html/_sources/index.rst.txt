.. StrEng documentation master file, created by
   sphinx-quickstart on Mon Oct  8 14:29:18 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

StrEng documentation!
==================================

A STRuctural ENGineering library.

.. .. image:: plantuml/out/streng/streng.svg

.. .. image:: plantuml/out/streng_codes/streng_codes.svg


.. .. raw:: html

..     <object data="plantuml/out/streng/streng.svg" type="image/svg+xml"></object>


.. uml::

   @startmindmap
   * streng
   ** codes
   ** common
   ** phd
   ** ppp
   ** tools
   ** xwflib
   @endmindmap





.. toctree::
    :maxdepth: 1
    :caption: Files structure

    pyfileslist
    rstfileslist


.. toctree::
    :maxdepth: 1
    :caption: Codes

    codes/eurocodes
    codes/greek
    codes/usa


.. toctree::
    :caption: Common
    :maxdepth: 1

    Input-Output <common/io>
    Math <common/math>


.. toctree::
    :caption: phd
    :maxdepth: 1

    Building Models <phd/building_models>
    Input Motions <phd/analyses>


.. toctree::
    :maxdepth: 1
    :caption: Pre-Post-Processing

    ppp/ppp


.. toctree::
    :maxdepth: 1
    :caption: Tools

    tools/tools


.. toctree::
    :maxdepth: 1
    :caption: Excel udfs library

    xwflib/xwflib



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
