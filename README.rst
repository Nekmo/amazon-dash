
.. image:: https://raw.githubusercontent.com/Nekmo/amazon-dash/master/amazon-dash.png
    :width: 100%

|

.. image:: https://img.shields.io/pypi/v/amazon-dash.svg?style=flat-square
  :target: https://pypi.org/project/amazon-dash/
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/amazon-dash.svg?style=flat-square
  :target: https://pypi.org/project/amazon-dash/
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/amazon-dash.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/amazon-dash
  :alt: Code Climate

.. image:: https://img.shields.io/requires/github/Nekmo/amazon-dash.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/amazon-dash/requirements/?branch=master
     :alt: Requirements Status


.. index::

Python Amazon Dash
##################
Hack your Amazon Dash to run what you want. Without welders. For the entire family.


1. Install Amazon Dash:

.. code:: bash

    sudo pip install amazon-dash


2. Use discovery mode to know the mac of your Dash (Run the program, and then press the button):

.. code:: bash

    sudo amazon-dash discovery


3. Create a config file (``amazon-dash.yml``):

.. code:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      0C:47:C9:98:4A:12:
        name: Hero
        user: nekmo
        cmd: spotify
      44:65:0D:48:FA:88:
        name: Pompadour
        user: nekmo
        cmd: kwrite


4. Run the daemon:

.. code:: bash

    sudo amazon-dash run

Contents
========
- `Avoid making a purchase by pressing the button <#avoid-making-a-purchase-by-pressing-the-button>`_.
- `Examples <#examples>`_
- `Troubleshooting <#troubleshooting>`_
- `References <#references>`_


Avoid making a purchase by pressing the button
==============================================
This program detects when your button connects to the network to execute actions, but does not prevent the ordering.

There are 3 ways to avoid making a purchase when you press the button.


Easy mode: Do not choose the product to buy when setting up
-----------------------------------------------------------
When you first set your button, you are asked which product you want to buy when you press the button. If you do not
choose an option, the button will work, but an order will not be created.

However, in order to take advantage of the free balance ($5/€5/£5), it is necessary to choose a product. The solution
is after ordering, deactivate the button, reconfigure it, and not choosing the product the second time.

However, you will receive an alert in the Amazon application every time you press the button asking you to finish the
configuration. You can turn off notifications, delete the application, or use another Amazon account.


Using an advanced router
------------------------
If you have an advanced router (DD-Wrt, Open-WRT, Tomato, RouterOS...), you can block Internet output from the buttons.
This is the preferred option. It is necessary to block the Internet output. Using DNS locks will not work. The button
uses its own DNS server IP, ignoring router DNS.


Raspberry PI solution
---------------------
You can use the Raspberry PI as a router if you have 2 network cards. The method is similar to the previous one, but
being a Linux system you can use iptables.


Examples
========
Here are some examples of how to use your Amazon Dash button:

* **Random Episode**: Play a random chapter of your favorite series, like *The Simpsons*, *Futurama*, *Friends*... https://github.com/Nekmo/random-episode


Troubleshooting
===============

Requirements and installation
-----------------------------
All dependencies are commonly used on a Linux system, but some may not be installed on your system. The dependencies
are:

* Python 2.7 or 3.4+.
* Python-pip (pip).
* Tcpdump.
* Sudo


Why root is required
====================
This program needs permission to open raw sockets on your system. You can set this permission using setcap, but you
must be very careful about who can run the program. Raw sockets permission could allow scaling permissions on the
system::

    setcap cap_net_raw=eip ./scripts/amazon-dash
    setcap cap_net_raw=eip /usr/bin/pythonX.X
    setcap cap_net_raw=eip /usr/bin/tcpdump

http://stackoverflow.com/questions/36215201/python-scapy-sniff-without-root

References
==========

* https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8#.gz0smxlv0
* https://github.com/vancetran/amazon-dash-rpi/blob/master/habits.py
* http://www.alphr.com/amazon/1001429/amazon-dash-button-hacks-5-ways-to-build-your-own-low-cost-connected-home/page/0/1
* https://community.smartthings.com/t/hack-the-amazon-dash-button-to-control-a-smartthings-switch/20427/14
