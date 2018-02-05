.. highlight:: console


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
  :target: https://codecov.io/github/Nekmo/amazon-dash
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/amazon-dash.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/amazon-dash/requirements/?branch=master
     :alt: Requirements Status



Python Amazon Dash
##################
Hack your Amazon Dash to run what you want. Without welders. For the entire family.

This program written in Python runs in daemon mode waiting for someone in the same
network to press a configured Amazon Dash button. It is not necessary to know
programming to use this program. Amazon-Dash executes **commands by command line,
calls a url and more**. This program works well on a **Raspberry PI** or on computers
with few resources.


1. **Install** Amazon Dash:

.. code::

    $ sudo pip install amazon-dash  # and after:
    $ sudo python -m amazon_dash.install

Also available on `AUR <https://aur.archlinux.org/packages/amazon-dash-git/>`_. See other installation methods
`in the documentation <http://docs.nekmo.org/amazon-dash/installation.html>`_.


2. Use *discovery mode* **to know the mac of your Dash** (Run the program, and then press any button):

.. code::

    $ sudo amazon-dash discovery


3. Edit **config file** (``/etc/amazon-dash.yml``):

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
      AC:63:BE:67:B2:F1:
        name: Kit Kat
        url: 'http://domain.com/path/to/webhook'
        method: post
        content-type: json
        body: '{"mac": "AC:63:BE:67:B2:F1", "action": "toggleLight"}'
      40:B4:CD:67:A2:E1:
        name: Fairy
        homeassistant: hassio.local
        event: toggle_kitchen_light


For more information see
`the documentation of the configuration file <http://docs.nekmo.org/amazon-dash/config_file.html>`_.


4. Run the **daemon**:

If you use a **Systemd** system (Debian 8+, Fedora 15+, Ubuntu 15.04+, Arch Linux 2012+, OpenSUSE 12.1+, and more)
execute::

    $ sudo systemctl start amazon-dash

To run Amazon-dash at startup::

    $ sudo systemctl enable amazon-dash


To run Amazon-dash manually look at `the documentation <http://docs.nekmo.org/amazon-dash/usage.html>`_.


5. **Avoid making a purchase** by pressing the button

This program detects when your button connects to the network to execute actions, but does not prevent the ordering.
The easiest way to avoid making a purchase is to reconfigure the button using the Amazon instructions
(by pressing the button for 5 seconds) but **skipping the last configuration step** *(do not choose which product you
want to associate with the button)*. If Amazon does not know what product you want, they can not charge anything on
your credit card.

There are two more methods `in the documentation <http://docs.nekmo.org/amazon-dash/avoid_purchase.html>`_.


Examples
========
Here are some examples of how to use your Amazon Dash button:

* **Random Episode**: Play a random chapter of your favorite series, like *The Simpsons*, *Futurama*, *Friends*... https://github.com/Nekmo/random-episode


References
==========

* https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8#.gz0smxlv0
* https://github.com/vancetran/amazon-dash-rpi/blob/master/habits.py
* http://www.alphr.com/amazon/1001429/amazon-dash-button-hacks-5-ways-to-build-your-own-low-cost-connected-home/page/0/1
* https://community.smartthings.com/t/hack-the-amazon-dash-button-to-control-a-smartthings-switch/20427/14
