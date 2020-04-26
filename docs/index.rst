Welcome to amazon-dash's documentation!
=======================================
Amazon Dash buttons are sold by Amazon to purchase certain products from their store. The buttons are sold for
$5/€5/£5 but Amazon gives you the money to spend on products. This project allows you to reprogram these buttons
purchased *"almost free"* to do what you want. To use this project you need a linux computer (for example a Raspberry
PI).

.. warning::
    Since 2020 your buttons can be **bricked** in an update from Amazon servers. Go to :ref:`future`
    for more info.


To **install** amazon-dash, run these commands in your terminal:

.. code-block:: console

    $ pip install amazon_dash
    $ sudo python -m amazon_dash.install

Actions supported in this project for your Amazon Dash buttons:

================================  ================================  ================================
.. image:: https://goo.gl/bq5QSK  .. image:: https://goo.gl/k4DJmf  .. image:: https://goo.gl/Gqo8W3
`System command`_                 `Call url`_                       `Homeassistant`_
.. image:: https://goo.gl/Cq4bYC  .. image:: https://goo.gl/L7ng8k
`OpenHAB`_                        `IFTTT`_
================================  ================================  ================================


Contents
--------

.. toctree::
   :maxdepth: 2

   readme
   installation
   future
   block_connections
   rescue
   usage
   config_file
   upgrade
   docker
   troubleshooting
   community
   modules
   contributing
   authors
   history
   references

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _System command: http://docs.nekmo.org/amazon-dash/config_file.html#execute-cmd
.. _Call url: http://docs.nekmo.org/amazon-dash/config_file.html#call-url
.. _Homeassistant: http://docs.nekmo.org/amazon-dash/config_file.html#homeassistant-event
.. _OpenHAB: http://docs.nekmo.org/amazon-dash/config_file.html#openhab-event
.. _IFTTT: http://docs.nekmo.org/amazon-dash/config_file.html#ifttt-event
