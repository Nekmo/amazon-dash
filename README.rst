
.. image:: https://raw.githubusercontent.com/Nekmo/amazon-dash/master/amazon-dash.png
    :width: 100%

|


.. image:: https://img.shields.io/travis/Nekmo/amazon-dash.svg?style=flat-square&maxAge=2592000
  :target: https://travis-ci.org/Nekmo/amazon-dash
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/amazon-dash.svg?style=flat-square
  :target: https://pypi.org/project/amazon-dash/
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/amazon-dash.svg?style=flat-square
  :target: https://pypi.org/project/amazon-dash/
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/amazon-dash.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/amazon-dash
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/amazon-dash/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/djangocms-comments
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/amazon-dash.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/amazon-dash/requirements/?branch=master
     :alt: Requirements Status



Python Amazon Dash
##################
Hack your Amazon Dash to run what you want. Without welders. For the entire family.

This program written in Python runs in daemon mode waiting for someone in the same
network to press a configured Amazon Dash button. It is not necessary to know
programming to use this program. Amazon-Dash executes commands by command line
or calls a url. This program works  well on a raspberry PI or on computers with
few resources.


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
        cmd: /opt/open-door kitcken
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        method: post
        content-type: json
        body: '{"mac": "AC:63:BE:67:B2:F1", "action": "toggleLight"}'


4. Run the daemon:

.. code:: bash

    sudo amazon-dash[ --config amazon-dash.yml] run

By default, `amazon-dash` will use the `amazon-dash.yml` file in the current directory with `sudo amazon-dash run`.
However, you can set the path to the file (for example, `/etc/amazon-dash.yml`) with `--config` parameter.
Please note that `--config` must be before `run`.


Contents
========
- `Avoid making a purchase by pressing the button <#avoid-making-a-purchase-by-pressing-the-button>`_.
- `Run at startup <#run-at-startup>`_
- `Examples <#examples>`_
- `Config file <#config-file>`_
- `Changelog <#changelog>`_
- `Troubleshooting <#troubleshooting>`_
- `Why Root is required <#why-root-is-required>`_
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


Run at startup
==============
This example is for systems with **Systemd**. The files of the services are in this `link <https://github.com/Nekmo/amazon-dash/tree/master/services>`_.
If your system is not supported, feel free to do a **pull request**.

1. Copy `amazon-dash.service` to `/etc/systemd/system/`.
2. Create your config file in `/etc/amazon-dash.yml`.
3. Enable your service with `sudo systemctl enable amazon-dash`.
4. Start your service with `sudo systemctl start amazon-dash`.


Examples
========
Here are some examples of how to use your Amazon Dash button:

* **Random Episode**: Play a random chapter of your favorite series, like *The Simpsons*, *Futurama*, *Friends*... https://github.com/Nekmo/random-episode


Config file
===========
The configuration file can be found anywhere but if the program runs in root mode,
it is necessary that only root can modify the file. This is a security measure to prevent
someone from executing commands as root using the program.

To change the permissions::

    sudo chmod 600 amazon-dash.yml
    sudo chown root:root amazon-dash.yml

The syntax of the configuration file is yaml. The configuration file has 2 main sections:

* **settings** (optional): common options.
* **devices** (required): The amazon dash devices.

The following options are available in **settings**:

* **delay** (optional): by default, 10. Minimum time that must pass between pulsations of the Amazon Dash button.

Each device is identified by the button **mac**. The mac can be obtained with the discovery command.
In the configuration of each button, there may be a way of execution. Only one execution method is allowed
for each device. The available exection methods are:

* **cmd**: local command line command. Arguments can be placed after the command.
* **url**: Call a url.

When the **cmd execution method** is used, the following options are available.

* **user**: System user that will execute the command. This option can only be used if Amazon-Dash is running as root.
* **cwd**: Directory in which the command will be executed.

When the **url execution method** is used, the following options are available.

* **method**: HTTP method. By default GET.
* **content-type** (*): HTTP Content-Type Header. Only available if Body is defined. If body is defined, default is form.
* **body**: Request payload. Only if the method is POST/PUT/PATCH. In json or form mode, the content must be a valid json. It is recommended to use single quotes before and after content in json.

(*) Content type aliases: `form = application/x-www-form-urlencoded`. `json = application/json`. `plain = text/plain`.

An example of a configuration file can be found at the beginning of the documentation.


Changelog
=========

v0.3.0
------

- Unit testing.
- Travis CI.
- Config validation.
- Help messages.
- Request to URL.
- Distinguish Amazon devices in discovery mode.


v0.2.0
------

- Securize config file.
- Systemd config file example.
- Refactor imports.
- Updated README.

v0.1.0
------

- Execute commands.
- Discovery mode.
- Setup.py
- README.


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
