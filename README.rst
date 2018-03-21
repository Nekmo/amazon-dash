

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

.. code:: console

    $ sudo pip install amazon-dash  # and after:
    $ sudo python -m amazon_dash.install

Also available on `AUR <https://aur.archlinux.org/packages/amazon-dash-git/>`_. See other installation methods
`in the documentation <http://docs.nekmo.org/amazon-dash/installation.html>`_.


2. Use *discovery mode* **to know the mac of your Dash** (Run the program, and then press any button):

.. code-block:: console

    $ sudo amazon-dash discovery


3. Edit **config file** (``/etc/amazon-dash.yml``):

.. code-block:: yaml

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
        confirmation: send-tg
      40:B4:CD:67:A2:E1:
        name: Fairy
        homeassistant: hassio.local
        event: toggle_kitchen_light
      18:74:2E:87:01:F2:
        name: Doritos
        openhab: 192.168.1.140
        item: open_door
        state: "ON"
    confirmations:
      send-tg:
        service: telegram
        token: '402642618:QwGDgiKE3LqdkNAtBkq0UEeBoDdpZYw8b4h'
        to: 24291592
        is_default: false


**UPGRADE** from `previous versions <http://docs.nekmo.org/amazon-dash/installation.html>`_

The following execution methods are supported with your Amazon Dash button with this program:

================================  ================================  ================================
.. image:: https://goo.gl/VqgMZJ  .. image:: https://goo.gl/a6TS7X  .. image:: https://goo.gl/zrjisq
`System command`_                 `Call url`_                       `Homeassistant`_
.. image:: https://goo.gl/Cq4bYC
`OpenHAB`_
================================  ================================  ================================


Amazon-dash also allows you to **send a confirmation** after pressing a button. You will also receive a message in
case of failure. Currently only **Telegram** is supported.


For more information see
`the documentation of the configuration file <http://docs.nekmo.org/amazon-dash/config_file.html>`_.


4. Run the **daemon**:

If you use a **Systemd** system *(Debian 8+, Fedora 15+, Ubuntu 15.04+, Arch Linux 2012+, OpenSUSE 12.1+, and more)*
execute:

.. code-block:: console

    $ sudo systemctl start amazon-dash

To run Amazon-dash at **startup**:

.. code-block:: console

    $ sudo systemctl enable amazon-dash


To run Amazon-dash manually look at `the documentation <http://docs.nekmo.org/amazon-dash/usage.html>`_.


5. **Avoid making a purchase** by pressing the button

This program detects when your button connects to the network to execute actions, but does not prevent the ordering.
The easiest way to avoid making a purchase is to reconfigure the button using the Amazon instructions
(by pressing the button for 5 seconds) but **skipping the last configuration step** *(do not choose which product you
want to associate with the button)*. If Amazon does not know what product you want, they can not charge anything on
your credit card.

There are two more methods `in the documentation. <http://docs.nekmo.org/amazon-dash/avoid_purchase.html>`_


Join the community
==================
Do you need ideas on how to use Amazon Dash? See what the community does with this project. Some examples:

* `The Simpsons Random Episode <http://docs.nekmo.org/amazon-dash/community.html#the-simpsons-random-episode>`_
* `Shopping list in Google Keep <http://docs.nekmo.org/amazon-dash/community.html#shopping-list-in-google-keep>`_
* `Play a audio <http://docs.nekmo.org/amazon-dash/community.html#play-a-audio>`_

See all the examples `in the community`_.


.. _System command: http://docs.nekmo.org/amazon-dash/config_file.html#execute-cmd
.. _Call url: http://docs.nekmo.org/amazon-dash/config_file.html#call-url
.. _Homeassistant: http://docs.nekmo.org/amazon-dash/config_file.html#homeassistant-event
.. _OpenHAB: http://docs.nekmo.org/amazon-dash/config_file.html#openhab-event
.. _in the community: http://docs.nekmo.org/amazon-dash/community.html
